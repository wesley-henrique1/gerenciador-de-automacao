from ..lib.settings import Relatorios, BaseDados, OutPut
from ..lib import MonitorETL, ValidarErros

import datetime as dt
import pandas as pd
import numpy as np
import os
import re

class auxiliar:
    def extrair_e_converter_peso(self,argumento):
        match = re.search(r'([\d\.,]+)\s*(KG|GR)', str(argumento), re.IGNORECASE)
        if match:
            valor_str = match.group(1).replace(',', '.')
            valor = float(valor_str)
            unidade = match.group(2).upper()
            if unidade == 'KG':
                return valor * 1000
            elif unidade == 'GR':
                return valor     
        return None
class Cadastro(auxiliar):
    validador = ValidarErros(fonte="Cadastro")
    def __init__(self):
        locWEB = r'z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\Wesley Henrique\CalibragemWeb.xlsx'
        self.list_path = [Relatorios._8596, BaseDados.EndFixo, locWEB]
        self.Retorno = [OutPut.Cadastro]
        self.chekout = [27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, 44]
        self.list_int = ['2-INTEIRO(1,90)', '1-INTEIRO (2,55)']
        self.list_div = ['6-PRATELEIRA','5-TERCO (0,46)','4-TERCO (0,56)']
        self.list_meio = ['3-MEDIO (0,80)', '7-MEIO PALETE']
        
        largura = 100
        comprimento = 120
        self.area_pl = (largura * comprimento) + 100
        self.alturaPK = 175
        self.Instancia = MonitorETL()

    def pipeline(self):
        try:
            self.Instancia.stageTime('Extract')
            colunas_origem = [
                "RUA"
                ,"PREDIO"
                ,"CODPROD"
                ,"OBS2"
                ,"ABASTECEPALETE"
                ,"CAPACIDADE"
                ,"PONTOREPOSICAO"
                ,"QTUNITCX"
                ,"ALTURAARM"
                ,"LARGURAARM"
                ,"COMPRIMENTOARM"
                ,'ALTURAM3'
                ,'LARGURAM3'
                ,'COMPRIMENTOM3'
                ,"LASTROPAL"
                ,"PK_END"
                ,"DESCRICAO"
                ,"QTTOTPAL"
                ,"ALTURAPAL"
                ,"CARACTERISTICA"
                ,"APTO"
                ,"TIPO_1"
            ]
            dados_prod = pd.read_excel(self.list_path[0], usecols= colunas_origem)
            endereco = pd.read_excel(self.list_path[1], sheet_name= 'STATUS', usecols= ["RUA", "TIPO_RUA", "CARACT"])
            dadosWEB = pd.read_excel(self.list_path[2], usecols= ['Código', 'MED_VENDA_DIAS_CX'])

            self.Instancia.stageTime('Extract')
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            self.Instancia.stageTime('Transform')
            dadosWEB = dadosWEB.rename(columns= {'Código':'CODWEB'}).fillna(0)

            TEMP = dados_prod.merge(endereco, on= 'RUA', how= 'inner')
            TEMP = TEMP.merge(dadosWEB, left_on= 'CODPROD', right_on= 'CODWEB', how= 'left')
            df_prod = TEMP.loc[TEMP['RUA'].between(1,39)].copy()
            dic_raname = {
                'ABASTECEPALETE' : 'FLEG_ABST'
                ,'CAPACIDADE' : 'CAP'
                ,'PONTOREPOSICAO' : 'P_REP'
                ,'QTUNITCX' : 'FATOR'
                ,'QTTOTPAL': 'PL'
            }
            df_PRODUTO = df_prod.rename(columns=dic_raname)
            df_PRODUTO['TESTE'] = df_PRODUTO['RUA'].astype(str) + " - " + df_PRODUTO['PREDIO'].astype(str)
            filtro = (df_PRODUTO['APTO'].between(100, 199)) & (df_PRODUTO['PK_END'].isin(self.list_meio))

            try:
                df_PRODUTO.loc[filtro, 'qt_meio'] = df_PRODUTO[filtro].groupby('TESTE')['TESTE'].transform('count')
                df_PRODUTO['FREQ_PROD'] = df_PRODUTO['TESTE'].map(df_PRODUTO['TESTE'].value_counts())

                df_PRODUTO['AREA_LT'] = round((df_PRODUTO['LARGURAARM'] * df_PRODUTO['COMPRIMENTOARM']) * df_PRODUTO['LASTROPAL'],0)
                df_PRODUTO['VolumeFRAC'] = df_PRODUTO['ALTURAM3'] * df_PRODUTO['LARGURAM3'] * df_PRODUTO['COMPRIMENTOM3']
                df_PRODUTO['VolumeMaster'] = df_PRODUTO['ALTURAARM'] * df_PRODUTO['LARGURAARM'] * df_PRODUTO['COMPRIMENTOARM']

                df_PRODUTO['GRAMATURA_GR'] = df_PRODUTO["DESCRICAO"].apply(self.extrair_e_converter_peso).fillna(0)
                df_PRODUTO['PL_LASTRO'] = df_PRODUTO['PL'] + df_PRODUTO['LASTROPAL']

                df_PRODUTO['ALTPL'] = df_PRODUTO['ALTURAARM'] * df_PRODUTO['ALTURAPAL']
                df_PRODUTO['V_ALTPL'] = np.where(
                    ((df_PRODUTO['ALTPL'] + df_PRODUTO['ALTURAARM']) < self.alturaPK) & (df_PRODUTO['MED_VENDA_DIAS_CX'] <= df_PRODUTO['LASTROPAL'])
                    ,"ABAIXO"
                    ,"ACIMA"
                )
            except Exception as e:
                self.validador.registrar_log(e, "T-SUPORTE")
            try:
                INT = (df_PRODUTO['FREQ_PROD'] <= 2) & (df_PRODUTO['PK_END'].isin(self.list_int))
                MEIO =(df_PRODUTO['qt_meio'] <= 2) & (df_PRODUTO['PK_END'].isin(self.list_meio))
                DIV = (df_PRODUTO['FREQ_PROD'] > 2)
                cond_status = [INT, MEIO, DIV]
                escolha_STATUS = ["INT","MEIO", "DIV"]
                df_PRODUTO['STATUS_PK'] = np.select(
                    cond_status
                    ,escolha_STATUS
                    ,default="VAL"
                )

                val_int1 = (df_PRODUTO['STATUS_PK'] == "INT") & (df_PRODUTO['V_ALTPL'] == 'ABAIXO') & (df_PRODUTO['CAP'] < df_PRODUTO['PL_LASTRO']) & (df_PRODUTO['FREQ_PROD'] > 1)
                val_int2 = (df_PRODUTO['STATUS_PK'] == "INT") & (df_PRODUTO['V_ALTPL'] == 'ACIMA') & (df_PRODUTO['CAP'] >= df_PRODUTO['PL_LASTRO']) & (df_PRODUTO['FREQ_PROD'] > 1)
                val_div = (df_PRODUTO['CAP'] > df_PRODUTO['PL']) & (df_PRODUTO['STATUS_PK'].isin(['MEIO', 'DIV']))

                escolha_cap = ['DIV_DOWN', 'DIV_UP', 'DIVERGENCIA']
                cond_cap = [val_int1, val_int2, val_div]

                abst_S = (df_PRODUTO['FLEG_ABST'] == 'NÃO') & (df_PRODUTO['STATUS_PK'] == "INT") & (df_PRODUTO['V_ALTPL'] == 'ABAIXO')
                abst_N = (df_PRODUTO['FLEG_ABST']== 'SIM') & ((df_PRODUTO['STATUS_PK'].isin(['DIV', 'MEIO'])) | (df_PRODUTO['V_ALTPL'] == 'ACIMA'))
                cond_abst = [abst_S, abst_N]

                rua_UN = (df_PRODUTO['TIPO_RUA'] == 'UN') & (df_PRODUTO['FATOR'] == 1)
                rua_CX = (df_PRODUTO['TIPO_RUA'] == 'CX') & (df_PRODUTO['FATOR'] != 1)
                cond_rua = [rua_UN, rua_CX]

                RuaGrandeza = (df_PRODUTO['TIPO_1'] == '1 - GRANDEZA') & (df_PRODUTO['RUA'].isin(self.chekout))
                RuaEmbalado = (df_PRODUTO['TIPO_1'] == '5 - EMBALADO') & (~df_PRODUTO['RUA'].isin(self.chekout))
                Cond_OS = [RuaGrandeza, RuaEmbalado]

                escolha = ['DIVERGENCIA', 'DIVERGENCIA']

                df_PRODUTO["V_CAP"] = np.select(
                    cond_cap
                    ,escolha_cap
                    ,default= "NORMAL"
                )
                df_PRODUTO['V_FLEG'] = np.select(
                    cond_abst
                    ,escolha
                    ,default= "NORMAL"
                )
                df_PRODUTO['V_RUA'] = np.select(
                    cond_rua
                    ,escolha
                    ,default= "NORMAL"
                )
                df_PRODUTO['V_TIPO_OS'] = np.select(
                    Cond_OS
                    ,escolha
                    ,default= 'NORMAL'
                )

                df_PRODUTO['V_AREA'] = np.where(
                    df_PRODUTO['AREA_LT'] > self.area_pl
                    ,"DIVERGENCIA"
                    ,"NORMAL"
                )
                df_PRODUTO['V_VOLUME'] = np.where(
                    (df_PRODUTO['VolumeFRAC'] * df_PRODUTO['FATOR']) > df_PRODUTO['VolumeMaster'],
                    "DIVERGENTE",
                    "NORMAL"
                )
                df_PRODUTO['V_CARACT'] = np.where(
                    df_PRODUTO['CARACTERISTICA'] != df_PRODUTO['CARACT']
                    ,"DIVERGENCIA"
                    ,"NORMAL"
                )
                df_PRODUTO['V_PESO'] = np.where(
                    (df_PRODUTO["GRAMATURA_GR"] >= 1000) & (df_PRODUTO['APTO'] > 200) & (~df_PRODUTO['RUA'].isin([31,32]))
                    ,"ACIMA DA BANDEJA"
                    ,"NORMAL"
                )
            except Exception as e:
                self.validador.registrar_log(e, "T-KPI")
                return False
            self.Instancia.stageTime('Transform')
        except Exception as e:
                self.validador.registrar_log(e, "Transform")
                return False
        try:
            self.Instancia.stageTime('Load')

            ordem_primaria = ['CODPROD', 'DESCRICAO','OBS2', 'RUA', 'PREDIO', 'APTO', 'TIPO_RUA','CARACTERISTICA']
            capacidade = ['FATOR','PL_LASTRO','PL','CAP', 'P_REP','FREQ_PROD','FLEG_ABST','STATUS_PK']
            validar = ['V_ALTPL', 'V_CAP', 'V_FLEG', 'V_CARACT', 'V_TIPO_OS', 'V_AREA', 'V_VOLUME', 'V_PESO', 'V_RUA']
            ordem_completa = ordem_primaria + capacidade + validar
            df_final = df_PRODUTO[ordem_completa]

            contagem = df_final['RUA'].nunique()
            misto = df_final['RUA'].loc[df_final['TIPO_RUA'] == 'MISTO'].nunique()
            caixa = df_final['RUA'].loc[df_final['TIPO_RUA'] == 'CX'].nunique()
            unitario = df_final['RUA'].loc[df_final['TIPO_RUA'] == 'UN'].nunique()

            pront_tt = df_final['CODPROD'].nunique()
            prod_caixa = df_final['CODPROD'].loc[df_final['FATOR'] == 1].nunique()
            prod_unitario = df_final['CODPROD'].loc[df_final['FATOR'] != 1].nunique()
            porcent_cx = round((prod_caixa / pront_tt) * 100, 2)
            porcent_un = round((prod_unitario / pront_tt) * 100, 2)

            df_amostradinho = pd.DataFrame({
                "CATEGORIA": ["RUAS", "PRODUTOS", "PERC_PROD (%)"],
                "CONTAGEM":  [contagem, pront_tt, 100],
                "MISTO":     [misto, 0, 0],
                "CAIXA":     [caixa, prod_caixa, porcent_cx],
                "UNITARIO":  [unitario, prod_unitario, porcent_un],
                "x":         ["x", "x", "x"]
            })
            df_final = df_final.sort_values(by=['RUA', 'PREDIO'], ascending= True)
            with pd.ExcelWriter(self.Retorno[0]) as var:
                df_final.to_excel(var, sheet_name= "cadastro", index= False)
                df_amostradinho.to_excel(var, sheet_name= "demostrativo", index= False)

            self.Instancia.stageTime('Load')
            self.Instancia.conversor(Modulo= "Cadastro")
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
