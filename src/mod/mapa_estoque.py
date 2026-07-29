# from ..lib.settings import Relatorios, Wms, ColNames, OutPut, BaseDados
# from ..lib import ValidarErros, MonitorETL

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.lib.settings import Relatorios, Wms, ColNames, OutPut, BaseDados
from src.lib import ValidarErros, MonitorETL

import datetime as dt
import pandas as pd
import numpy as np
import os

class auxiliar:
    def categorizar_AE(self, Rua_AE, Rua_AP, map_dic):
        try:
            r_ae = int(Rua_AE)
            r_ap = int(Rua_AP)
        except:
            return "--"

        if r_ae == r_ap:
            return "DT"
        excecoes = map_dic.get(r_ap, [])
        
        if (r_ae in excecoes) or (abs(r_ae - r_ap) == 1):
            return "VZ"
        
        return "FR"
    def ajuste_numeros(self, data_frame, colunas):
        for col in colunas:
            data_frame[col] = (
                data_frame[col]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            data_frame[col] = (
                pd.to_numeric(data_frame[col], errors="coerce")
                .fillna(-1)
                .astype(float)
            )
        return data_frame

    pass
class MapaEstoque(auxiliar):
    validador = ValidarErros(fonte="Mapa Estoque")
    def __init__(self):
        self.list_path = [Wms.geral07, Relatorios._8596, BaseDados.EndFixo]
        self.Retorno = [OutPut.MapaEstoque]
        self.VIRTUAIS = [60, 70, 80, 100, 106, 44, 47, 40]
        self.estruturas = {
            "INTEIRO (2,55)": [255, "INT_255"]
            ,"INTEIRO(1,90)": [190, "INTEIRO"]
            ,"INTEIRO(1,35)": [135, "MEDIO"]
            ,"MEDIO (0,80)": [80, "PONTA"]
            ,"TERCO (0,56)": [56, "PONTA"]
            ,"TERCO (0,46)": [46, "PONTA"]
        }
        self.DataFrame = pd.DataFrame({
            "PL_END": ["INTEIRO (2,55)","INTEIRO(1,90)","INTEIRO(1,35)","MEDIO (0,80)","TERCO (0,56)","TERCO (0,46)"]
            ,"CM": [255, 190, 135, 80, 56, 46]
            ,"CLASSE_AE": ["INT_255", "INTEIRO", "MEDIO","PONTA","PONTA", "PONTA"]
        })
        self.map_ruas = {
            13: [12]
            ,14: [15,44]
            ,30: [28,29]
            ,31: [13,14,15,16,17,18,19,32,44]
            ,32: [13,14,15,16,17,18,19,31,44]
            ,33: [34,35,36,37,38,39]
            ,34: [33,35,36,37,38,39]
            ,35: [33,34,36,37,38,39]
            ,36: [33,34,35,37,38,39]
            ,37: [33,34,35,36,38,39]
            ,38: [33,34,35,36,37,39]
            ,39: [33,34,35,36,37,38]
        }
    
        self.Instancia = MonitorETL()
        pass

    def pipeline(self):
        try:
            self.Instancia.stageTime('Extract')
            indices = [0, 1, 2, 3, 4, 6, 7, 9, 10, 11, 12, 16, 17, 18, 19, 20]
            base_geral = pd.read_csv(
                self.list_path[0]
                ,header= None
                ,usecols= indices
                ,names= [ColNames.Geral[i] for i in indices]
                ,sep=','
            )            
            R_8596 = pd.read_excel(
                self.list_path[1]
                ,usecols= ['CODPROD',"RUA", 'ALTURAARM', 'QTUNITCX', "QTTOTPAL"]
            )
            end_parado = pd.read_excel(self.list_path[2], sheet_name= 'AE', usecols= ['COD_END','TIPO'])
            self.Instancia.stageTime('Extract')
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            self.Instancia.stageTime('Transform')
            base_geral['QTDE'] = base_geral['QTDE'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)
            base_geral['DISP_'] = base_geral['DISP_'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)

            aereos_1707 = base_geral.loc[(base_geral['TIPO_END'] == "AE") & (~base_geral['RUA'].isin(self.VIRTUAIS))].copy()
            R_8596 = R_8596.loc[~R_8596['RUA'].isin(self.VIRTUAIS)]
            prod = R_8596.rename(columns= {
                "RUA": "RUA_AP"
            })
            end_parado = end_parado.rename(columns= {"TIPO":'PL_END'})

            prod['QTUNITCX'] = pd.to_numeric(prod['QTUNITCX'], errors= 'coerce').fillna(0).astype(int) 
            prod['QTTOTPAL'] = pd.to_numeric(prod['QTTOTPAL'], errors= 'coerce').fillna(0).astype(int) 
            prod['PL_UN'] = prod['QTTOTPAL'] * prod['QTUNITCX']

            df_completo = aereos_1707.merge(prod, on='CODPROD', how= 'left')
            df_completo = df_completo.merge(end_parado, on= 'COD_END', how= 'left')
            df_completo = df_completo.merge(self.DataFrame, on= 'PL_END', how= 'left')

            df_completo['PL_ALT'] = df_completo['CAMADA'] * df_completo['ALTURAARM']
            df_completo['DISP_CX'] = df_completo['DISP_'] / df_completo['QTUNITCX']
            df_completo['CAMADA_AE'] = np.ceil(df_completo['DISP_CX'] / df_completo['LASTRO'])
            df_completo['DISP_ALT'] = df_completo['CAMADA_AE'] * df_completo['ALTURAARM']
            df_completo['STATUS'] = np.where(
                df_completo['CODPROD'] > 0
                ,"OCUPADO"
                ,"VAZIO"
            )
                    
            CAT_cond = [
                df_completo['CODPROD'] == 0
                ,df_completo['DISP_ALT'] <= 80
                ,df_completo['DISP_ALT'] <= 135
                ,df_completo['DISP_ALT'] <= 190
                ,df_completo['DISP_ALT'] <= 255
                ,df_completo['DISP_ALT'] > 255
            ]
            CAT_result = [
                "VAZIO"
                ,"PONTA"
                ,"MEDIO"
                ,"INTEIRO"
                ,"INT_255"
                ,"ACIMA_VALIDAR"
            ]
            df_completo['CATEGORIA'] = np.select(CAT_cond, CAT_result, default= '--')

            val = (
                (df_completo['CATEGORIA'] =='PONTA') 
                & (df_completo['CM'] > 135)
            )
            DIV_cond = (
                (df_completo['DISP_'] < df_completo['PL_UN']) 
                & val
            )
            df_completo['DIVERGENCIA'] = np.where(DIV_cond, "VERIFICAR", "CORRETO")

            col_int = ['RUA', 'RUA_AP']
            for col in col_int:
                df_completo[col] = pd.to_numeric(df_completo[col], errors= 'coerce').fillna(0).astype(int)

            df_completo['LOC_AEREO'] = df_completo.apply(
                lambda x: self.categorizar_AE(x['RUA'], x['RUA_AP'], self.map_ruas), 
                axis= 1
            )
            fase = base_geral.loc[base_geral['CODPROD'] > 0]
            fase['QTDE_AP'] = np.where(fase['TIPO_END'] == 'AP', 1, 0)
            fase['QTDE_AE'] = np.where(fase['TIPO_END'] == 'AE', 1, 0)

            condicoes = [
                fase['RUA'].isin(list(range(1, 14))),
                fase['RUA'].isin(list(range(14, 31)) + [40]),
                fase['RUA'].isin(list(range(31, 40)) + [44] + list(range(200, 204)))
            ]

            escolhas = ['Fase 1', 'Fase 2', 'Fase 3']
            fase['Fases'] = np.select(condicoes, escolhas, default= 'Fora')

            grupoFase = fase.groupby('Fases').agg(
                QTDE_AP= ('QTDE_AP', 'sum'),
                QTDE_AE= ('QTDE_AE', 'sum'),
            ).reset_index()
            grupoFase['TOTAL'] = grupoFase['QTDE_AP'] + grupoFase['QTDE_AE']
            grupoRua = fase.groupby(['RUA','Fases']).agg(
                QTDE_AP= ('QTDE_AP', 'sum'),
                QTDE_AE= ('QTDE_AE', 'sum'),
            ).reset_index()
            grupoRua['TOTAL'] = grupoRua['QTDE_AP'] + grupoRua['QTDE_AE']            

            self.Instancia.stageTime('Transform')
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            self.Instancia.stageTime('Load')
            etapa_1 = [
                'CODPROD'
                ,'DESCRICAO'
                ,'RUA_AP'
                ,'COD_END'
                ,'RUA'
                ,'PREDIO'
                ,'NIVEL'
                ,'APTO'
                ,'PL_END'
                ,'STATUS'
                ,'CLASSE_AE'
            ]
            etapa_2 = [
                'QTDE'
                ,'ENTRADA'
                ,'SAIDA'
                ,'DISP_'
            ]
            etapas_KPI  = [
                'DISP_CX'
                ,'PL_ALT'
                ,'DISP_ALT'
                ,'CAMADA_AE'
                ,'CATEGORIA'
                ,'LOC_AEREO'
                ,'DIVERGENCIA'
            ]
            df_completo = df_completo[etapa_1 + etapa_2 + etapas_KPI]
            df_completo = df_completo.sort_values(by=["RUA", "PREDIO"], ascending= True)
            print("\nsave")
            print(df_completo.head(3))
            print(grupoRua.head(3))
            with pd.ExcelWriter(self.Retorno[0], engine= 'openpyxl') as var:
                df_completo.to_excel(var , index= False, sheet_name="Analitico")
                grupoFase.to_excel(var, index= False, startrow= 0,sheet_name="FasesINV")
                grupoRua.to_excel(var, index= False, startrow= len(grupoFase) + 1 + 3, sheet_name="FasesINV")

            self.Instancia.stageTime('Load')
            self.Instancia.conversor(Modulo= "Mapa Estoque")
            return True
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False
    def carregamento(self, validar):
        lista_de_logs = []
        try:
            if not validar:
                return
            for contador, path in enumerate(self.list_path, 1):
                data_file = os.path.getmtime(path)
                nome_file = os.path.basename(path)

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
            dic_retorno = []
            return lista_de_logs, dic_retorno
        except Exception as e:
            self.validador.registrar_log(e, "CARREGAMENTO")
            return False
    def outputLog(self, validar):
        ListaOutPut = []
        try:
            if not validar:
                return
            for path in self.Retorno:
                data_file = os.path.getmtime(path)
                nome_file = os.path.basename(path)

                data_modificacao = dt.datetime.fromtimestamp(data_file)
                data_formatada = data_modificacao.strftime('%d/%m/%Y')
                horas_formatada = data_modificacao.strftime('%H:%M:%S')

                Dicionario = {
                    "ARQUIVO": nome_file,
                    "DATA": data_formatada,
                    "HORA": horas_formatada
                }
                ListaOutPut.append(Dicionario)
            return ListaOutPut, path
        except Exception as e:
            self.validador.registrar_log(e, "output")
            return False


if __name__ == "__main__":
    instancia = MapaEstoque()
    instancia.pipeline()