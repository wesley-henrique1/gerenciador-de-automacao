from src.lib.settings import Relatorios, OutPut
from src.lib.valerros import ValidarErros

from datetime import datetime as dt
from pathlib import Path

import pandas as pd
import numpy as np


class auxiliar:
    pass

class DownUp(auxiliar):
    validador = ValidarErros(fonte="Baixas_retorno")
    def __init__(self):
        self.list_path = [Relatorios._8628, Relatorios._8596]
        self.Retorno = [OutPut.downUp]
        pass

    def pipeline(self):
        try:
            col_baixas = ['DATA','NUMOS', 'CODPROD', 'ENDERECO_ORIG', 'NIVEL','NIVEL_1','RUA','RUA_1', 'CODROTINA', 'Tipo O.S.', 'QT']
            col_dados = ['CODPROD', 'DESCRICAO', 'RUA', 'PREDIO', 'APTO', 'CAPACIDADE']

            dataBaixas = pd.read_excel(self.list_path[0], usecols= col_baixas)
            dataDados = pd.read_excel(self.list_path[1], usecols= col_dados)
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            ruasAtivas = dataDados.loc[dataDados['RUA'].between(1, 39)].copy()
            ruasAtivas['PRODUTO'] = ruasAtivas['CODPROD'].astype(str) + " - " + ruasAtivas['DESCRICAO']

            dataBaixas['TIPO'] = dataBaixas['Tipo O.S.'].str.split('-').str[0].fillna(0).astype(int)
            corte = dataBaixas.loc[
                (dataBaixas['CODROTINA'].isin([1723,1709])) 
                & (dataBaixas['TIPO'] == 58) 
                & (dataBaixas['CODPROD'].isin(ruasAtivas['CODPROD']))
                & (dataBaixas['RUA'] != 50) 
                & (dataBaixas['RUA_1'] != 50)
            ].copy()
            baixas = (corte['NIVEL'].between(2, 9)) & (corte['NIVEL_1'] == 1)
            subida = (corte['NIVEL'] == 1) & (corte['NIVEL_1'].between(2, 9))

            corte['TIPO_OS'] = np.select([baixas, subida], ['DOWN', 'UP'], default= 'FORA')
            corte['AUX_DOWN'] = np.where(corte['TIPO_OS'] == 'DOWN', corte['QT'], 0)
            corte['AUX_UP'] = np.where(corte['TIPO_OS'] == 'UP', corte['QT'], 0)
            corte = corte.sort_values(by= 'DATA', ascending= True).drop_duplicates(subset= 'NUMOS', keep= 'last')
            corte = corte.drop(columns= ['Tipo O.S.', 'RUA_1'])
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            with pd.ExcelWriter(self.Retorno[0], engine= 'openpyxl') as var:
                ruasAtivas.to_excel(var, sheet_name= "Cadastro", index= False)
                corte.to_excel(var, sheet_name= "baixas", index= False)
            return True
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False

    def carregamento(self, validar):
        lista_de_logs = []
        ListRetorno = []
        try:
            if not validar or not self.list_path:
                return lista_de_logs, ListRetorno 
                
            for contador, Arquivo in enumerate(self.list_path, 1):
                Arquivo = Path(Arquivo)
                data_file = Arquivo.stat().st_mtime
                nome_file = Arquivo.name

                data_modificacao = dt.fromtimestamp(data_file)
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
        
        try:
            if not validar or not self.Retorno:
                return ListaOutPut, "PULAR"   
                         
            for Arquivo in self.Retorno:
                Arquivo = Path(Arquivo)
                data_file = Arquivo.stat().st_mtime
                nome_file = Arquivo.name

                data_modificacao = dt.fromtimestamp(data_file) 
                data_formatada = data_modificacao.strftime('%d/%m/%Y')
                horas_formatada = data_modificacao.strftime('%H:%M:%S')

                Dicionario = {
                    "ARQUIVO": nome_file,
                    "DATA": data_formatada,
                    "HORA": horas_formatada
                }
                ListaOutPut.append(Dicionario)
                
            return ListaOutPut, Arquivo
            
        except Exception as e:
            self.validador.registrar_log(e, "output")
            return ListaOutPut, "PULAR"

