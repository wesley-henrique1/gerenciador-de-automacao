from ..lib.settings import Wms, ColNames, OutPut
from ..lib.Tratar286 import BaseDados286
from ..lib.valerros import ValidarErros

import datetime as dt
from pathlib import Path
import pandas as pd
import numpy as np

class auxiliar:
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
        
class ContagemETL(auxiliar):
    validador = ValidarErros(fonte="Mapa Estoque")
    def __init__(self):
        self.ancora286 = BaseDados286()
        self.caminhoINV = Path(r"Z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.6 - PCL Cadastro\Wesley Henrique\base_inv")
        self.booleanoSave = False

        self.ListaCaminhos = [Wms.endereco07]
        self.ListaCaminhos.extend(self.ancora286.RetornoBase())
        self.ListOutPut = [OutPut.InvSave]

        pass
    def pipeline(self):
        try:
            listaAR = []
            col = ['Dep.', 'Rua', 'Prédio', 'Nível', 'Apto.', 'Código', 'Descrição', 'Inventário']
            col_286 = ['Código', 'Estoque', 'Qtde Pedida']

            for arquivo in self.caminhoINV.glob("*xls*"):
                if not arquivo.name.startswith("~$"):
                    df = pd.read_excel(arquivo, header= 1, usecols= col)
                    listaAR.append(df)
            if not listaAR:
                return
            
            dfInvetario = pd.concat(listaAR, axis= 0, ignore_index=True)
            estoque = self.ancora286.Pipeline(colcheck= col_286)
            endereco = pd.read_csv(self.ListaCaminhos[0], header= None, names= ColNames.Endereco)
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            endereco = endereco.rename(columns= {'COD': 'CODPROD'})
            grupoAereos = endereco.loc[endereco['TIPO_PK'] == 'AE'].groupby(['CODPROD']).agg(
                QTDE_AE = ('TIPO_PK', 'count'),
                END_AE = ('DISP', 'sum')
            ).reset_index()
            apartamentos = endereco[['CODPROD','TIPO_PK', 'ENTRADA', 'SAIDA', 'DISP']].loc[endereco['TIPO_PK'] == 'AP']

            dfInvetario = dfInvetario.rename(columns= {'Código': 'CODPROD'})

            dfCompleto = dfInvetario.merge(estoque, on= 'CODPROD', how= 'left')
            dfCompleto = dfCompleto.merge(apartamentos, on= 'CODPROD', how= 'left')
            dfCompleto = dfCompleto.merge(grupoAereos, on= 'CODPROD', how= 'left')
            dfCompleto = dfCompleto.drop(columns= ['Dep.', 'Nível', 'Descrição','TIPO_PK'])
            for coluna in ['ESTOQUE', 'DISPONIVEL', 'TOTALBLOQ', 'ENTRADA', 'SAIDA', 'DISP']:
                dfCompleto[coluna] = dfCompleto[coluna].apply(self.converter_numero_seguro)

            dfCompleto = dfCompleto.fillna(value={'QTDE_AE': 0, 'END_AE': 0})
            dfCompleto['SaldoProd'] = dfCompleto['Inventário'] + dfCompleto['DISP'] 

            try:
                dfCompleto['Pendente'] = np.where(
                    dfCompleto['ENTRADA'].astype(float) + dfCompleto['SAIDA'].astype(float),
                    "Sim", "Não"
                )
                gerCritico = (dfCompleto['SaldoProd'] == 0) & (dfCompleto['DISPONIVEL'] > 0) 
                GerInferior = dfCompleto['SaldoProd'] < dfCompleto['DISPONIVEL']
                GerSuperior = dfCompleto['SaldoProd'] > dfCompleto['DISPONIVEL']
                GerNeutro = dfCompleto['SaldoProd'] == dfCompleto['DISPONIVEL']
                dfCompleto['BaixoEST'] = np.select(
                    [gerCritico, GerInferior, GerSuperior, GerNeutro], 
                    ["Critico", "Inferior", "Superior", "Neutro"], 
                    default= 'Anomalias'
                )

                ProdZerado = (dfCompleto['ESTOQUE'] == 0) & (dfCompleto['PEDIDO'] == 0) &  (dfCompleto['Inventário'] == 0)
                ProdCritico = (dfCompleto['ESTOQUE'] == 0) &  (dfCompleto['Inventário'] != 0)
                ProdFora = (dfCompleto['ESTOQUE'] > 0) | (dfCompleto['PEDIDO'] > 0)
                
                dfCompleto['CATEGORIA'] = np.select(
                    [ProdZerado, ProdCritico, ProdFora], 
                    ['Zerados', 'Criticos','Estoque/Pedido'], 
                    default= 'Anomalias'
                )
            except Exception as e:
                self.validador.registrar_log(e, "T_metricas")
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            dfCompleto.to_excel(self.ListOutPut[0], sheet_name= "Inventario", index= False)
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
        ListaOutPut = []
        var = None
        try:
            if not validar:
                return ListaOutPut 
                
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
                ListaOutPut.append(Dicionario)
            return ListaOutPut, var
            
        except Exception as e:
            self.validador.registrar_log(e, "output")
            return ListaOutPut, Arquivo