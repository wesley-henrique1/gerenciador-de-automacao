import datetime as dt
from pathlib import Path

import pandas as pd
import numpy as np

from ..lib.settings import Relatorios, Wms, OutPut, ColNames
from ..lib import ValidarErros, MonitorETL, Tratar286

class Auxiliar:
    def converter_numero_seguro(self, val):
        if isinstance(val, (int, float)):
            return float(val) if pd.notna(val) else 0.0
        
        val_str = str(val).strip()
        if val_str.lower() in ['nan', '', 'none']:
            return 0.0
        
        if ',' in val_str and '.' in val_str:
            val_str = val_str.replace('.', '').replace(',', '.')
        elif ',' in val_str:
            val_str = val_str.replace(',', '.')
        elif val_str.count('.') > 1:
            val_str = val_str.replace('.', '')
            
        try:
            return float(val_str)
        except ValueError:
            return 0.0
        except Exception as e:
            if hasattr(self, 'validador'):
                self.validador.registrar_log(e, "286_numeros")
            return False
class Acuracidade(Auxiliar):
    validador = ValidarErros(fonte="Acuracidade")   
    def __init__(self):
        self.ancora = Tratar286.BaseDados286()
        self.Instancia = MonitorETL()

        self.ListaCaminhos = [Wms.gerencial07, Wms.endereco07, Relatorios._8596]
        self.ListaCaminhos.extend(self.ancora.RetornoBase())
        self.ListOutPut = [OutPut.Acuracidade]

        self.pipeline()

    def pipeline(self):
        try:
            self.Instancia.stageTime('Extract')
            df_bloq = self.ancora.Pipeline()
            end_ger = pd.read_csv(self.ListaCaminhos[0], header=None, names=ColNames.Gerencial)  
            df_end = pd.read_csv(self.ListaCaminhos[1], header=None, names=ColNames.Endereco)
            df_prod = pd.read_excel(self.ListaCaminhos[2], usecols=['CODPROD', 'QTUNITCX', 'QTTOTPAL'])
            self.Instancia.stageTime('Extract')
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            self.Instancia.stageTime('Transform')
            
            end_ger = end_ger.rename(columns={'COD': "CODPROD"})
            end_ger['RUA'] = end_ger['RUA'].fillna(0).astype(int)

            df_end = df_end.rename(columns={"COD": "CODPROD"})
            df_end = df_end[['CODPROD', 'ENTRADA', 'SAIDA', 'DISP', 'QTDE']].loc[df_end['TIPO_PK'] == "AE"]
            
            cols_to_convert = ['CODPROD', 'ENTRADA', 'SAIDA', 'DISP', 'QTDE']
            for col in cols_to_convert:
                df_end[col] = df_end[col].apply(self.converter_numero_seguro)
            
            grupo_end = df_end.groupby('CODPROD').agg(
                SAIDA=('SAIDA', 'sum'),
                ENTRADA=('ENTRADA', 'sum'),
                QT_DISP=('DISP', 'sum'),
                QTDE=('QTDE', 'sum'),
            ).reset_index()

            df_prod['CODPROD'] = df_prod['CODPROD'].fillna(0).astype(int)

            dfCompleto = end_ger.loc[end_ger['RUA'].between(1, 39)]
            dfCompleto = dfCompleto.merge(df_bloq, on='CODPROD', how='left')
            dfCompleto = dfCompleto.merge(grupo_end, on='CODPROD', how='left')
            dfCompleto = dfCompleto.merge(df_prod, on='CODPROD', how='left')

            dfCompleto.drop(columns=['EMBALAGEM'], inplace=True)

            cols_metricas = ['ENDERECO', 'PICKING', 'CAP', 'QTUNITCX', 'ENTRADA', 'SAIDA', 'QTDE', 'QT_DISP']
            for col in cols_metricas:
                dfCompleto[col] = dfCompleto[col].apply(self.converter_numero_seguro)

            dfCompleto['DIF_UN'] = dfCompleto['ENDERECO'] - dfCompleto['ESTOQUE']
            dfCompleto['DIF_CX'] = round(dfCompleto['DIF_UN'] / dfCompleto['QTUNITCX'], 1)
            dfCompleto['ENDERECO'] = dfCompleto['ENDERECO'] + dfCompleto['ENTRADA']
            dfCompleto['CAP_CONVERTIDA'] = dfCompleto['CAP'] * dfCompleto['QTUNITCX']

            cols_numericas = ['PICKING', 'CAP_CONVERTIDA', 'DIF_CX', 'DIF_UN', 'RUA', 'PREDIO', 'DISPONIVEL']
            for col in cols_numericas:
                dfCompleto[col] = pd.to_numeric(dfCompleto[col], errors='coerce').fillna(0)

            # --- CRIAÇÃO DAS COLUNAS CATEGORIZADAS ---
            try:
                dfCompleto['VAL_ESTOQUE'] = np.where(dfCompleto['DISPONIVEL'].between(1, 40), "VALIDAR", "NORMAL")
                dfCompleto['PENDENCIA'] = np.where(dfCompleto['QTDE_O.S'] > 0, 'FOLHA', 'INVENTARIO')

                cond_dif = [
                    dfCompleto['DIF_CX'] == 0,
                    (dfCompleto['DIF_CX'] > 0) & (dfCompleto['DIF_CX'] < 5),
                    (dfCompleto['DIF_CX'] >= 5) & (dfCompleto['DIF_CX'] < 10),
                    dfCompleto['DIF_CX'] >= 10,
                    (dfCompleto['DIF_CX'] < 0) & (dfCompleto['DIF_CX'] > -5),
                    (dfCompleto['DIF_CX'] <= -5) & (dfCompleto['DIF_CX'] > -10),
                    dfCompleto['DIF_CX'] <= -10
                ]
                dfCompleto['CATEGORIA_DIF'] = np.select(cond_dif, [0, 1, 2, 3, -1, -2, -3], default=99)

                cond_op = [
                    dfCompleto['DIF_UN'] < 0,
                    dfCompleto['DIF_UN'] > 0,
                    dfCompleto['DIF_UN'] == 0,
                ]
                dfCompleto["TIPO_OP"] = np.select(cond_op, ["END_MENOR", "END_MAIOR", "CORRETO"], default="-")

                cond_ap = [
                    dfCompleto['PICKING'] > dfCompleto['CAP_CONVERTIDA'],
                    dfCompleto['PICKING'] < 0,
                    dfCompleto['PICKING'] == 0
                ]
                dfCompleto['AP_VS_CAP'] = np.select(cond_ap, ['AP_MAIOR', "AP_NEGATIVO", "CORRETO"], default="-")
                
            except Exception as e:
                self.validador.registrar_log(e, "T_Metricas")
                return False
            
            df_prod = df_prod.drop_duplicates(subset='CODPROD', keep='first')
            dfCompleto = dfCompleto.sort_values(by=['RUA', 'PREDIO'], ascending=True)
            self.Instancia.stageTime('Transform')  
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            self.Instancia.stageTime('Load')
            dfCompleto = dfCompleto.drop(columns= ['DESC','GERENCIAL','DEP','NIVEL'])
            with pd.ExcelWriter(self.ListOutPut[0]) as var:
                dfCompleto.to_excel(var, index= False, sheet_name= 'DIVERGENCIA')
                df_prod.to_excel(var, index= False, sheet_name= 'DIM_PROD')

            self.Instancia.stageTime('Load')
            self.Instancia.conversor(Modulo="Acuracidade")
            return True
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False

    def carregamento(self, validar):
        lista_de_logs = []
        ListRetorno = []
        try:
            if not validar:
                return lista_de_logs, ListRetorno 
                
            for contador, Arquivo in enumerate(self.ListaCaminhos, 1):
                Arquivo = Path(Arquivo)
                data_file = Arquivo.stat().st_mtime
                nome_file = Arquivo.name

                data_modificacao = dt.datetime.fromtimestamp(data_file)
                data_formatada = data_modificacao.strftime('%d/%m/%Y')
                horas_formatada = data_modificacao.strftime('%H:%M:%S')

                dic_log = {
                    "CONTADOR" : contador
                    ,"ARQUIVO" : nome_file
                    ,"DATA" : data_formatada
                    ,"HORAS" : horas_formatada
                }
                lista_de_logs.append(dic_log)
                
            return lista_de_logs, ListRetorno
        except Exception as e:
            self.validador.registrar_log(e, "CARREGAMENTO")
            return lista_de_logs, ListRetorno
    def outputLog(self, validar):
        ListaOut = []
        var = None
        try:
            if not validar:
                return ListaOut 
                
            for Arquivo in self.ListOutPut:
                Arquivo = Path(Arquivo)
                data_file = Arquivo.stat().st_mtime
                nome_file = Arquivo.name
                var = Arquivo
                data_modificacao = dt.datetime.fromtimestamp(data_file) 
                data_formatada = data_modificacao.strftime('%d/%m/%Y')
                horas_formatada = data_modificacao.strftime('%H:%M:%S')

                Dicionario = {
                    "ARQUIVO": nome_file,
                    "DATA": data_formatada,
                    "HORA": horas_formatada
                }
                ListaOut.append(Dicionario)
            return ListaOut, var
            
        except Exception as e:
            self.validador.registrar_log(e, "output")
            return ListaOut, Arquivo