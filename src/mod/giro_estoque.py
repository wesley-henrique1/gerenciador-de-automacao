from ..lib.settings import Relatorios, Filial_18, Wms, ColNames, OutPut
from ..lib import ValidarErros, MonitorETL, Tratar286

import pandas as pd
import numpy as np
import datetime as dt
import warnings
import os
warnings.simplefilter(action='ignore', category=UserWarning)

class GiroEstoque:
    validador = ValidarErros(fonte="main_logica")
    def __init__(self):
        self.hoje = dt.datetime.now()
        self.dias = 30
        self.VIRTUAIS = [0,60, 70, 80, 100, 106, 44]

        self.list_path = [
            Relatorios._8596,Filial_18._8596,Wms.endereco07
        ]
        self.Retorno = [OutPut.GiroStatus]
        self.Instancia = MonitorETL()
        self.Instancia286 = Tratar286.BaseDados286()
        pass
    def pipeline(self):
        try:
            self.Instancia.stageTime('Extract')
            col_8596 = [
                'DTULTENT', 'DTULTSAIDA', 'CODPROD', 'DESCRICAO', 'OBS2', 'QTUNITCX', 'RUA', 'PREDIO', 'NIVEL', 'APTO','QTESTGER'
            ]

            col_1707 = [5,13]
            _col_ = ColNames.Endereco

            dados_F11 = pd.read_excel(self.list_path[0], usecols= col_8596)            
            dados_F18 = pd.read_excel(self.list_path[1], usecols= col_8596)
            aux_1707 = pd.read_csv(self.list_path[2], header= None, usecols= col_1707, names=[_col_[5], _col_[13]])
            df_estoque = self.Instancia286.Pipeline(colcheck= ['Custo ult. ent.', 'Reservado', 'Comprador'])
            
            self.Instancia.stageTime('Extract')
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            self.Instancia.stageTime('Transform')
            try:
                col_zero = [
                    'Custo ult. ent._x', 'Custo ult. ent._y'
                    ,'Reservado_x','Reservado_y'
                ]
                for col in col_zero:
                    df_estoque[col] = pd.to_numeric(df_estoque[col]).fillna(0)

                condicoes = [
                    df_estoque["Custo ult. ent._x"] > df_estoque["Custo ult. ent._y"]
                    ,df_estoque["Custo ult. ent._x"] < df_estoque["Custo ult. ent._y"]
                ]
                resultados = [
                    "F11"
                    ,"F18"
                ]
                res_custo = [
                    round(df_estoque["Custo ult. ent._x"],2)
                    ,round(df_estoque["Custo ult. ent._y"],2)
                ]

                c_x = df_estoque['Comprador_x'].fillna(0)
                c_y = df_estoque['Comprador_y'].fillna(0)

                compr_cond = [
                    (c_x == c_y)
                    ,(c_x == 0) & (c_y != 0)
                    ,(c_x != 0) & (c_y == 0)
                    ,(c_x != c_y)
                ]
                compr_resultados = [
                    df_estoque['Comprador_x']
                    ,df_estoque['Comprador_y']
                    ,df_estoque['Comprador_x']
                    ,df_estoque['Comprador_x']
                ]

                df_estoque["FILIAL"] = np.select(condicoes, resultados, default= "F11-F18")
                df_estoque["CUSTO"] = np.select(
                    condicoes, res_custo
                    ,default= round(df_estoque["Custo ult. ent._x"],2)
                )
                df_estoque['COMPRADOR'] = np.select(compr_cond, compr_resultados, default="VERIFICAR")

                nomes_separados = df_estoque['COMPRADOR'].str.split()

                df_estoque['COMPRADOR'] = np.where(
                    nomes_separados.str.len() > 1
                    ,nomes_separados.str[0] + " " + nomes_separados.str[-1]
                    ,nomes_separados.str[0]        
                )
                df_estoque['RESERVADO'] = round(df_estoque['Reservado_x'] + df_estoque['Reservado_y'])
                df_estoque['CUSTO_EST'] = round(df_estoque["CUSTO"] * df_estoque["DISPONIVEL"], 2)
                df_estoque['_RESERVA_'] = np.where(
                    df_estoque['RESERVADO'] > 0
                    ,"S"
                    ,"N"
                )
                
                drop_x = ["Reservado_x","Custo ult. ent._x","Comprador_x"]
                drop_y = ["Reservado_y","Custo ult. ent._y","Comprador_y"]
                df_estoque = df_estoque.drop(columns= drop_x + drop_y)
                pass
            except Exception as e:
                self.validador.registrar_log(e, "T_286")
                return False
            try:
                virtual_prod = dados_F11.loc[(dados_F11['RUA'].isin(self.VIRTUAIS))].copy()
                dados_F11 = dados_F11.loc[(~dados_F11['RUA'].isin(self.VIRTUAIS))].copy()

                dados_F18 = dados_F18.loc[(dados_F18['QTESTGER'] > 0) & (~dados_F18['CODPROD'].isin(virtual_prod['CODPROD']))].copy()
                dados_F18 = dados_F18[['CODPROD', 'DTULTSAIDA', 'DTULTENT']]

                dados_prod = dados_F11.merge(dados_F18, on= 'CODPROD', how= "outer")

                col_int = ['QTUNITCX','RUA','PREDIO','APTO']
                dt_col = ["DTULTSAIDA_x", "DTULTSAIDA_y", "DTULTENT_x", "DTULTENT_y"]

                for col in col_int:
                    dados_prod[col] = pd.to_numeric(dados_prod[col], errors= 'coerce').fillna(0).astype(int)

                for col in dt_col:
                    dados_prod[col] = pd.to_datetime(dados_prod[col], dayfirst= True, errors= 'coerce')

                dados_prod = dados_prod.loc[~dados_prod['RUA'].isin(self.VIRTUAIS)].copy()

                dados_prod['DT_SAIDA'] = dados_prod[['DTULTSAIDA_x', 'DTULTSAIDA_y']].max(axis=1)
                dados_prod['DT_ENTRADA'] = dados_prod[['DTULTENT_x', 'DTULTENT_y']].max(axis=1)
                dados_prod['OBS2'] = dados_prod['OBS2'].fillna("ATIVO")
                dados_prod['DIAS_S'] = (self.hoje - dados_prod['DT_SAIDA']).dt.days.fillna(0).astype(int)
                dados_prod['DIAS_E'] = (self.hoje - dados_prod['DT_ENTRADA']).dt.days.fillna(0).astype(int)
                dados_prod['PARADO'] = np.where(
                    (dados_prod['DIAS_S'] > 30) & (dados_prod['DIAS_E'] > 30)
                    ,"S"
                    ,"N"
                )
                dados_prod = dados_prod.drop(columns=["DTULTSAIDA_x", "DTULTENT_x", "DTULTSAIDA_y", "DTULTENT_y", "QTESTGER"])

                pass
            except Exception as e:
                self.validador.registrar_log(e, "T_8596")
                return False
            try:
                aux = aux_1707.loc[aux_1707['TIPO_PK'] == 'AE']
                grupo_AE = aux.groupby("COD").agg(
                    QT_AE = ('TIPO_PK', 'count')
                ).reset_index()
                grupo_AE['QT_AE'] = grupo_AE['QT_AE'].astype(int)

                pass
            except Exception as e:
                self.validador.registrar_log(e, "T_1707")
                return False

            df_completo = dados_prod.merge(df_estoque, on='CODPROD', how='left')

            bloq_quest = [
                (df_completo['TOTALBLOQ'] > 0) & (df_completo['DISPONIVEL'] == 0)
                ,(df_completo['TOTALBLOQ'] > 0) & (df_completo['DISPONIVEL'] > 0)
                ,(df_completo['TOTALBLOQ'] == 0) & (df_completo['DISPONIVEL'] > 0)
            ]
            bloq_result = [
                "TOTAL"
                ,"PARCIAL"
                ,"LIVRE"
            ]

            categoria_cond = [
                (df_completo['DIAS_S'] > 30) & (df_completo['DIAS_E'] > 30) & (df_completo['DISPONIVEL'] > 0) 
                ,df_completo['DISPONIVEL'] > 0
                ,df_completo['ESTOQUE'] == 0
            ]
            categoria_result = [
                "PARADO"
                ,"ATIVOS"
                ,"INATIVO"
            ]

            df_completo['STATUS_BLOQUEIO'] = np.select(bloq_quest, bloq_result, default= "--")
            df_completo['CATEGORIAS'] = np.select(categoria_cond, categoria_result, default= "BLOQUEADO")

            df_completo = df_completo.merge(grupo_AE, left_on= 'CODPROD', right_on= "COD", how= 'left').drop(columns='COD')
            df_completo = df_completo.sort_values(by= ['RUA', 'PREDIO', 'APTO'])

            df_ativos = df_completo.loc[df_completo['OBS2'] =="ATIVO"].copy()
            df_FL = df_completo.loc[df_completo['OBS2'] =="FL"].copy()
            
            self.Instancia.stageTime('Transform')
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            self.Instancia.stageTime('Load')
            with pd.ExcelWriter(self.Retorno[0]) as destino:
                df_ativos.to_excel(destino, sheet_name= "ATIVOS", index= False)
                df_FL.to_excel(destino, sheet_name= "FLs", index= False)
                df_completo.to_excel(destino, sheet_name= "COMPLETO", index= False)

            self.Instancia.stageTime('Load')
            self.Instancia.conversor(Modulo= "Giro Estoque")
            return True
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False
        
    def carregamento(self, validar):
        lista_de_logs = []
        valor = self.Instancia286.RetornoBase()
        self.list_path.extend(valor)
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
