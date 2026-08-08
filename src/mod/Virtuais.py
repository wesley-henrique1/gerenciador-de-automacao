from src.lib.settings import Relatorios, OutPut
from src.lib import Tratar286, BuscarAVIND, ValidarErros

import datetime as dt
import pandas as pd
import numpy as np
import os


class VirtualBase:
    validador = ValidarErros(fonte= "Virtual")
    def __init__(self):
        self.hoje = pd.to_datetime('today').normalize()
        self.ancoraEST = Tratar286.BaseDados286()
        self.ancoraAV = BuscarAVIND.ConsolidarAVIND()

        self.list_path = [Relatorios._8596]
        self.list_path.extend(self.ancoraEST.RetornoBase())
        self.list_path.extend(self.ancoraAV.BaseDados())

        self.Retorno = [OutPut.Jupyter_2]
        pass
    def pipeline(self):
        try: 
            col_8596 = ['DTULTSAIDA', 'DTULTENT', 'QTESTGER', 'CODPROD', 'DESCRICAO', 'RUA', 'PREDIO', 'NIVEL', 'APTO']
            baseDados = pd.read_excel(self.list_path[0], usecols= col_8596)
            estoque = self.ancoraEST.Pipeline(colcheck= ['Fora de linha'])
            baseAV = self.ancoraAV.Consolidar(retirarCol= ['DESCRICAO','RUA', 'PREDIO', 'APTO'])
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False
        try:
            estoque['OBSFL'] = estoque['Fora de linha_x'].replace('Falso', 'Ativo').replace('Verdadeiro', 'FL')
            estoque = estoque.drop(columns= ['Fora de linha_y', 'Fora de linha_x'])

            Dfdados = baseDados.merge(estoque, on= 'CODPROD', how= 'left').drop(columns= ['DESC'])
            Dfdados = Dfdados.merge(baseAV, on= 'CODPROD', how= 'left')
            try:
                Dfdados = Dfdados.loc[Dfdados['RUA'].between(60,70)]
                Dfdados['DTULTENT'] = pd.to_datetime(Dfdados['DTULTENT'], dayfirst=True, errors='coerce')
                Dfdados['DTULTSAIDA'] = pd.to_datetime(Dfdados['DTULTSAIDA'], dayfirst=True, errors='coerce')
                Dfdados['DiasSaida'] = self.hoje - Dfdados['DTULTSAIDA']
                Dfdados['DiasEntrada'] = self.hoje - Dfdados['DTULTENT'] 

                NOVOS = (Dfdados['DTULTSAIDA'].isna()) & (Dfdados['DTULTENT'].isna())
                BLOQUEADOS = (Dfdados['ESTOQUE'] > 0) & (Dfdados['TOTALBLOQ'] >= Dfdados['ESTOQUE'])
                LIVRES = (Dfdados['ESTOQUE'] > 0) & (Dfdados['DISPONIVEL'] > 0)
                ZERADOS = (Dfdados['ESTOQUE'] == 0) & (Dfdados['TOTALBLOQ'] == 0)
                NEGATIVOS = Dfdados['DISPONIVEL'] <0

                catResultado = ["Introdução", "Bloqueado", "Disponivel", "Zerado", 'Negativo']
                Dfdados['CATEGORIAS'] = np.select([NOVOS, BLOQUEADOS, LIVRES, ZERADOS, NEGATIVOS], catResultado, default= '-')
                Dfdados = Dfdados.fillna({"SaldoIND": 0, "SaldoAV": 0, "AV_IND": 0})
            except Exception as e:
                self.validador.registrar_log(e, "T_Categorizar")
            try:
                DfRetiradas = Dfdados.loc[(Dfdados['OBSFL'] == 'FL') & (Dfdados['CATEGORIAS'] == 'Zerado')]
                dfNomalias = Dfdados.loc[(Dfdados['OBSFL'] == 'FL') & (Dfdados['ESTOQUE'] > 0) & (Dfdados['RUA'] == 70)]
                dftroca = Dfdados.loc[(Dfdados['OBSFL'] != 'FL') & (Dfdados['RUA'] == 70)]

                codigos_todos = pd.concat([DfRetiradas['CODPROD'], dfNomalias['CODPROD'], dftroca['CODPROD']])
                foraFiltro = Dfdados.loc[~Dfdados['CODPROD'].isin(codigos_todos.drop_duplicates())]
            except Exception as e:
                self.validador.registrar_log(e, "T_Separação")
        except Exception as e:
                self.validador.registrar_log(e, "Transform")
                return False
        try:
            resumo = pd.DataFrame([
                {"Métrica": "QTDE Retirada",  "Quantidade": DfRetiradas['CODPROD'].nunique()},
                {"Métrica": "QTDE Estoque70", "Quantidade": dfNomalias['CODPROD'].nunique()},
                {"Métrica": "QTDE Ativos70",  "Quantidade": dftroca['CODPROD'].nunique()},
                {"Métrica": "Qtde Restantes", "Quantidade": foraFiltro['CODPROD'].nunique()}
            ])
            col_list = ['DTULTSAIDA', 'DTULTENT', 'QTESTGER', 'CODPROD', 'DESCRICAO', 'OBSFL', 'RUA', 'PREDIO', 'NIVEL', 'APTO', 'CATEGORIAS']

            with pd.ExcelWriter(self.Retorno[0]) as save:
                DfRetiradas[col_list].to_excel(save, index= False, sheet_name="Retirada")
                dfNomalias.to_excel(save, index= False, sheet_name="Estoque70")
                dftroca.to_excel(save, index= False, sheet_name="Ativos70")
                foraFiltro.to_excel(save, index= False, sheet_name= "Restantes")
                resumo.to_excel(save, index= False, sheet_name= "Resumo")
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
