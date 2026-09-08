from ..lib.settings import Wms, BaseDados, ColNames, OutPut
from ..lib import ValidarErros, MonitorETL

import datetime as dt
import pandas as pd
import numpy as np
import glob
import re
import os 
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text

import warnings
warnings.simplefilter(action='ignore', category=UserWarning)

class __auxiliares:
    def cosultar_db(self, consulta):
        try:
            connection_url = URL.create(
            "access+pyodbc",
            query={"odbc_connect":  self.ODBC_CONN_STR}
            )
            self.engine = create_engine(connection_url)
            db_dados = pd.read_sql(text(consulta), self.engine)
            return db_dados
        except Exception as e:
            self.validador.registrar_log(e, "Consulta_banco_dados")
            return pd.DataFrame()
    def atualizar(self, df, tabela):
        try:            
            df.to_sql(
                name= tabela
                ,con= self.engine
                ,if_exists='append'
                ,index=False
                ,chunksize=1000
            )
        except Exception as e:
            self.validador.registrar_log(e, f"Load_{tabela}")
            return False         
    def extrair_e_ordenar_data(self, df, data):
        var = df.copy()

        var['dia'] = var[data].dt.day_name('pt_BR')
        var['mes'] = var[data].dt.month_name('pt_BR')
        var['ano'] = var[data].dt.year
        var[data] = var[data].dt.strftime("%d-%m-%Y")    
        var = var.sort_values(by= data, ascending= True, axis= 0)
        return var
    def ajustar_numero(self, df_copia, coluna, tipo_dados):
        def ajustar(valor):
            if pd.isna(valor) or valor is None:
                return 0.0
            valor = str(valor).strip()
            if isinstance(valor, str):
                if valor.count('.') >= 1 and ',' in valor: 
                    valor = valor.replace('.', '').replace(',', '.')
                elif ',' in valor:
                    valor = valor.replace(',', '.')
            try:
                if tipo_dados == int:
                    return int(float(valor))
                elif tipo_dados == float:
                    return round(float(valor), 2)
            except (ValueError, TypeError):
                return 0.0
        df_copia[coluna] = df_copia[coluna].apply(ajustar)
        return df_copia
class Corte(__auxiliares):
    validador = ValidarErros(fonte="Corte")
    def __init__(self):
        DRIVER = BaseDados.drive
        DB_PATH = BaseDados.path_acumulado
        self.NOME_TABELA = BaseDados.DBPedidos
        self.ODBC_CONN_STR = (f"DRIVER={DRIVER};" f"DBQ={DB_PATH};")

        self.list_path = [Wms._1767]
        self.Retorno = [OutPut.Corte]
        self.BaseCorte = BaseDados._8041
        self.ano = dt.datetime.now().year

        self.Instancia = MonitorETL()

    def pipeline(self):
        try:
            self.Instancia.stageTime('Extract')
            files_pedidos = glob.glob(os.path.join(self.BaseCorte, '*.xls*'))

            query_select = f"SELECT {'NOME_ARQUIVO'} FROM {self.NOME_TABELA}"
            names_db = self.cosultar_db(query_select)
            arquivos_processados = set(names_db['NOME_ARQUIVO'].str.strip().tolist())

            df_corte = pd.read_csv(self.list_path[0],header= None, names= ColNames._1767)
            self.Instancia.stageTime('Extract')
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            self.Instancia.stageTime('Transform')
            try:
                df_corte['hora'] = df_corte['hr'].astype(str) + ':' + df_corte['min'].astype(str)
                df_corte['data'] = pd.to_datetime(df_corte['data'], format= '%d/%m/%y').sort_index(axis= 0, ascending= True)
                df_corte['hora'] = pd.to_datetime(df_corte['hora'], format= '%H:%M').dt.strftime('%H:%M')

                col_ajustar = ['vl_corte', 'qtde_corte']
                for col in col_ajustar:
                    df_corte = self.ajustar_numero(df_corte, col, float)
                df_corte = df_corte.sort_values(by="data", ascending= True, axis= 0)
            except Exception as e:
                self.validador.registrar_log(e, "CORTE_GERAL")
                return False
            try:
                df_dia = df_corte.loc[df_corte['hora'].between("07:30:00", "18:00:00")].copy()

                var_dia = df_dia.groupby('data').agg(
                            vl_corte=('vl_corte', 'sum'),
                            qtde_corte=('qtde_corte', 'count'),
                            qtde_item=('cod', 'nunique')
                        ).reset_index()
                
                var_dia = self.extrair_e_ordenar_data(var_dia, 'data')
                var_dia['vl_corte'] = var_dia['vl_corte'].round(2).astype(str).str.replace('.', ',', regex= False)
                var_dia = var_dia.sort_values(by= 'data', ascending= True, axis= 0)
            except Exception as e:
                self.validador.registrar_log(e, "CORTE_DIA")
                return False
            try:
                df_noite = df_corte.loc[~df_corte['hora'].between("07:30:00", "18:00:00")].copy()

                df_noite['data'] = pd.to_datetime(df_noite['data'], format= '%d/%m/%Y')
                df_noite["data_turno"] = df_noite['data'].copy()
                df_noite.loc[df_noite['hora'] < "07:30:00", 'data_turno'] -= pd.Timedelta(days=1)
                var_noite = df_noite.groupby('data_turno').agg(
                    vl_corte=('vl_corte', 'sum'),
                    qtde_corte=('qtde_corte', 'count'),
                    qtde_item=('cod', 'nunique')
                ).reset_index()
                var_noite = self.extrair_e_ordenar_data(var_noite, 'data_turno')
                var_noite['vl_corte'] = var_noite['vl_corte'].round(2).astype(str).str.replace('.', ',', regex= False)
                var_noite = var_noite.sort_values(by='data_turno', ascending= True, axis= 0)
            except Exception as e:
                self.validador.registrar_log(e, "CORTE_NOITE")
                return False
            try:
                list_achados = []
                lis_procurados = []
                list_erros = []
                    
                for file in files_pedidos:
                    name_file = os.path.basename(file)
                    if name_file in arquivos_processados:
                        list_achados.append(name_file)
                        continue
                    try:
                        df_var = pd.read_excel(file)
                        pedido = df_var['NUMPED'].nunique()
                        produto = df_var['PRODUTO'].nunique()

                        data_extraida = re.search(r'(\d{2}[-_]\d{2})', name_file).group(1)
                        data_arrumada = data_extraida.replace('_', '-') + f"-{self.ano}"
                        data_final = pd.to_datetime(data_arrumada, format='%d-%m-%Y')
                        novo_nome_arquivo = f"PEDIDOS_{data_arrumada}.xlsx"

                        df_pedidos = pd.DataFrame({
                            "NOME_ARQUIVO" : [novo_nome_arquivo],
                            "QTDE_PED"     : [pedido],
                            "QTDE_PROD"    : [produto],
                            "DATA"         : [data_final]
                        })
                        lis_procurados.append(df_pedidos)
                    except Exception as e:
                        list_erros.append(name_file)
                        self.validador.registrar_log(e, f"{name_file}: P-leitura")
                    try:
                        novo_caminho_completo = os.path.join(self.BaseCorte, novo_nome_arquivo)
                        os.rename(file, novo_caminho_completo)
                    except Exception as e:
                        self.validador.registrar_log(e, "Renomear Arquivo")      
                if lis_procurados:
                    df_final = pd.concat(lis_procurados, ignore_index=True)
                    self.atualizar(df_final, self.NOME_TABELA)

                    query_dados = f"SELECT {'*'} FROM {self.NOME_TABELA}"
                    db_dados = self.cosultar_db(query_dados)
                else :
                    query_dados = f"SELECT {'*'} FROM {self.NOME_TABELA}"
                    db_dados = self.cosultar_db(query_dados)
            except Exception as e:
                self.validador.registrar_log(e, "PEDIDOS")
                return False          
            try:
                df_div = df_corte[['data','desc','hora', 'n_ped']].copy()
                df_div['data'] = pd.to_datetime(df_div['data'], format= '%d/%m/%Y')
                df_div["data_turno"] = df_div['data'].copy()
                df_div.loc[df_div['hora'] < "07:30:00", 'data_turno'] -= pd.Timedelta(days=1)

                var_div = df_div.groupby('data_turno').agg(
                    ped_imperfeito=('n_ped', 'nunique')
                ).reset_index()
                var_div['data_turno'] = pd.to_datetime(var_div['data_turno'], format='%d-%m-%Y')
                var_div = var_div.merge(db_dados, left_on= 'data_turno', right_on= 'DATA', how= 'left').drop(columns= {'NOME_ARQUIVO', 'QTDE_PROD'}).sort_values(by="data_turno", ascending= True, axis= 0)
            except Exception as e:
                self.validador.registrar_log(e, "DIVERGENCIAS")
                return False
            self.Instancia.stageTime('Transform')
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            self.Instancia.stageTime('Load')
            max_ex_dia= df_dia['data'].max() 
            max_ex_noite = df_noite['data_turno'].max()

            ex_dia = df_dia.loc[df_dia['data'] == max_ex_dia].copy()
            ex_noite = df_noite.loc[df_noite['data_turno'] == max_ex_noite].copy()
            
            with pd.ExcelWriter(self.Retorno[0]) as destino_corte:
                df_corte.to_excel(destino_corte, sheet_name='extrato', index= False)
                ex_dia.to_excel(destino_corte, sheet_name= 'ex_dia', index= False)
                ex_noite.to_excel(destino_corte, sheet_name= 'ex_noite', index= False)

            self.qt_files = len(lis_procurados)
            self.qt_erros = len(list_erros)
            self.qtde = len(list_achados)
            self.dia = var_dia
            self.noite = var_noite
            self.divergencia = var_div
            self.Instancia.stageTime('Load')
            self.Instancia.conversor(Modulo= "Corte")
            return True
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False
        
    def Log_Retorno(self):
        try:
            self.dia['data'] = pd.to_datetime(self.dia['data'], format='%d-%m-%Y')
            self.noite['data_turno'] = pd.to_datetime(self.noite['data_turno'], format='%d-%m-%Y')
            self.divergencia['DATA'] = pd.to_datetime(self.divergencia['DATA'], format='%d-%m-%Y')

            apresentar_final = self.dia.merge(self.noite, left_on='data',right_on='data_turno', how='outer', suffixes=('_DIA', '_NOITE'))
            apresentar_final['data'] = np.where(apresentar_final['data'].isna(),apresentar_final['data_turno'],apresentar_final['data'])

            apresentar_final = apresentar_final.merge(self.divergencia, left_on='data',right_on='DATA', how='left')
            
            col_int = ["qtde_corte_DIA","qtde_corte_NOITE","qtde_item_DIA","qtde_item_NOITE", "QTDE_PED", "ped_imperfeito"]
            for col in col_int:
                apresentar_final[col] = apresentar_final[col].fillna(0).astype(int)
        
            data = ['data']
            valor_corte =['vl_corte_DIA', 'vl_corte_NOITE']
            corte = ['qtde_corte_DIA', 'qtde_corte_NOITE']
            qtde = ['qtde_item_DIA', 'qtde_item_NOITE']
            pedido_col = ['QTDE_PED', 'ped_imperfeito']
            col_nova = data + valor_corte + corte + qtde + pedido_col
            apresentar_final = apresentar_final[col_nova].copy().fillna(0)
            apresentar_final['dia'] = apresentar_final['data'].dt.day_name('pt_BR')
            apresentar_final['mes'] = apresentar_final['data'].dt.month_name('pt_BR')
            apresentar_final['ano'] = apresentar_final['data'].dt.year

            titulo = (
                f"|{"DATA":^12} |"
                f" {"VL_CORTE":^19} |" 
                f" {"QTDE DIA E NOITE":16} |"
                f" {"PEDIDO":^10} |"
                f" {"DIVERGENCIA":^11} |"
                f" {"CORTE DIA E NOITE":^17} |" 
                f" {"DIA":<13} |"
                f" {"MES":<10} |"
                f" {"ANO":<4} |\n"
                f"{"-" * 139}\n"

            )
            tabela = ""
            for celula in apresentar_final.itertuples():
                data_formatada = celula.data.strftime('%d-%m-%Y') if hasattr(celula.data, 'strftime') else str(celula.data)
                
                celula_vl = f"{celula.vl_corte_DIA:^8} - {celula.vl_corte_NOITE:^8}"
                celula_qt = f"{celula.qtde_corte_DIA:^4} - {celula.qtde_corte_NOITE:^4}"
                celula_item = f"{celula.qtde_item_DIA:^4} - {celula.qtde_item_NOITE:^4}"
                linhas = (
                    f"|{data_formatada:<12} |"
                    f" {celula_vl:^18} |"
                    f" {celula_qt:^16} |"
                    f" {str(celula.QTDE_PED):^10} |"
                    f" {str(celula.ped_imperfeito):^11} |"
                    f" {celula_item:^17} |"
                    f" {celula.dia:<13} |"
                    f" {celula.mes:<10} |"
                    f" {celula.ano:<4} |\n"
                )
                tabela += linhas

            return titulo + tabela
        except Exception as e:
            self.validador.registrar_log(e, "Log_retorno")
            return False
    def carregamento(self, validar):
        lista_de_logs = []
        dicRetorno = []
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
            
            dic = {
                "MODULO": "Corte"
                ,"ARQUIVOS": self.qt_files
                ,"ERROS": self.qt_erros
                ,"LEITURA": self.qtde 
            }
            dicRetorno.append(dic)
            return lista_de_logs, dicRetorno
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
