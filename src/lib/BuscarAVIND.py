import pandas as pd
from ..lib import ValidarErros
from ..lib.settings import Relatorios
import numpy as np
import glob
import os
import io
import msoffcrypto

class ConsolidarAVIND:
    validador = ValidarErros(fonte="Avaria|Indenizado")

    def __init__(self):
        self.pastaIND = r'Z:\1 - CD Dia\4 - Equipe PCL\6.6 - Recuperação e Indenizado\6.6.2 - WMS - Controle Indenizado\2026\INDENIZADO QUINZENAL 2026'
        self.FileAvaria = r'z:\1 - CD Dia\4 - Equipe PCL\6.6 - Recuperação e Indenizado\6.6.1 - WMS - Controle Avaria\2026\Controle de Bloqueados na avaria.xlsx'

        self.PontoPartida = None
        self.senhaIND = 'IND202501'
        self.Nome_Planilha = "LANÇAMENTOS"
        pass
    
    def BaseDados(self):
        lista = [self.FileAvaria, self.pastaIND]
        return lista
    def DadosIND(self):
        try:
            DictDiretorios = {}
            chavesPasta = []
            pastas = [p for p in glob.glob(os.path.join(self.pastaIND, "*")) if os.path.isdir(p)]
            for nome in pastas:
                nomePATH = os.path.basename(nome)
                var = nomePATH.split('-')
                chave = var[0].strip()
                DictDiretorios[chave] = nome

                try:
                    chavesPasta.append(int(chave))
                except ValueError:
                    chavesPasta.append(chave)

            maior_chave = max(chavesPasta)
            caminho_da_maior_pasta = DictDiretorios[str(maior_chave)]
            arquivos_encontrados = glob.glob(os.path.join(caminho_da_maior_pasta, "Controle Indenizado*.xls*"))
            pass
        except Exception as e:
            self.validador.registrar_log(e, "BaseIndenizado")
        try:
            listnext = []
            resumo = []

            colunas = ["DATA","COD PRODUTO","DESCRIÇÃO","EMBALAGEM","QT","MOTIVO","TIPO","PRÉDIO"]

            if not arquivos_encontrados:
                return pd.DataFrame()
            for next_ in arquivos_encontrados:
                try:
                    nomeAR = os.path.basename(next_)
                    with io.BytesIO() as gaveta:
                        with open(next_, "rb") as arquivo:
                            data = msoffcrypto.OfficeFile(arquivo)
                            data.load_key(password=self.senhaIND)
                            data.decrypt(gaveta)

                        gaveta.seek(0)

                        excel = pd.ExcelFile(gaveta)
                        NameColunm = excel.sheet_names

                        if self.Nome_Planilha in NameColunm:
                            temporario = pd.read_excel(excel, sheet_name= self.Nome_Planilha, usecols=colunas)
                            listnext.append(temporario)
                            resumo.append({"Arquivo": nomeAR, "Total": temporario["COD PRODUTO"].nunique(), "Link": next_})
                except Exception as e:
                    print(f"Erro no arquivo {nomeAR}: {e}")
                    resumo.append({"Arquivo": nomeAR, "Total": 0, "Link": e})

            if listnext:
                data = pd.concat(listnext, axis=0, ignore_index=True)
                data = data.drop_duplicates()
                data = data.dropna(subset=["COD PRODUTO"])
                data['CODPROD'] = pd.to_numeric(data['COD PRODUTO'], errors= 'coerce')
            else:
                data = pd.DataFrame()
                print("Nenhuma planilha válida foi processada - IND.")
        except Exception as e:
            self.validador.registrar_log(e, "Extração_excel_ind")
        try:
            data['Entrada'] = np.where(data['TIPO'].str.contains(r'entradas?$', case= False, na= False), data['QT'].abs(), 0)
            data['Saida'] = np.where(data['TIPO'].str.contains(r'sai?das?$', case=False, na=False), data['QT'].abs(), 0)
            data['datinha'] = pd.to_datetime(data['DATA'], errors= 'coerce')
            GrupoIND = data.groupby(['CODPROD']).agg(
                ENTRADA = ('Entrada', 'sum'),
                SAIDA = ('Saida', 'sum'),
                IND_DT = ('datinha', 'max')
            ).reset_index()
            GrupoIND['SaldoIND'] = GrupoIND['ENTRADA'] - GrupoIND['SAIDA']

            self.PontoPartida == "IND"
            return GrupoIND
        except Exception as e:
            self.validador.registrar_log(e, "Finalização_ind")
            return False
    def DadosAV(self):
        try: 
            data = pd.read_excel(self.FileAvaria, sheet_name= 'LANÇAMENTOS', usecols= ['DATA', 'COD PRODUTO', 'QUANT', 'TIPO'])
            data = data.dropna(subset= 'COD PRODUTO')
        except Exception as e:
            self.validador.registrar_log(e, "baseAvaria")
        try: 
            data['CODPROD'] = pd.to_numeric(data['COD PRODUTO'], errors= 'coerce')
            data['Entrada'] = np.where(data['TIPO'].str.contains(r'entradas?$', case= False, na= False), data['QUANT'].abs(), 0)
            data['Saida'] = np.where(data['TIPO'].str.contains(r'sai?das?$', case=False, na=False), data['QUANT'].abs(), 0)
            data['datinha'] = pd.to_datetime(data['DATA'], errors= 'coerce')
        except Exception as e:
            self.validador.registrar_log(e, "TratamentoAV")
        try:
            grupoAV = data.groupby('CODPROD').agg(
                ENTRADA = ('Entrada', 'sum'),
                SAIDA = ('Saida', 'sum'),
                AV_DT = ('datinha', 'max')
            ).reset_index()
            grupoAV['SaldoAV'] =  grupoAV['ENTRADA'] - grupoAV['SAIDA'] 

            self.PontoPartida = "AV"
            return grupoAV 
        except Exception as e:
            self.validador.registrar_log(e, "TratamentoAV")
    def Consolidar(self, retirarCol = None):
        try:
            dfAvaria = self.DadosAV() 
            dfIdenizado = self.DadosIND()
            dados = pd.read_excel(Relatorios._8596, usecols= ["CODPROD", "DESCRICAO", "RUA"	, "PREDIO", "APTO"])

            filtroAV = dfAvaria.drop(columns= ['ENTRADA', 'SAIDA'])
            filtroIND = dfIdenizado.drop(columns= ['ENTRADA', 'SAIDA'])

            dadosFim = dados.merge(filtroAV, on= 'CODPROD', how='left')
            dadosFim = dadosFim.merge(filtroIND, on= 'CODPROD', how='left')

            dadosFim = dadosFim.loc[(dadosFim['AV_DT'].notna()) | (dadosFim['IND_DT'].notna())]
            dadosFim = dadosFim.fillna({'SaldoIND': 0, 'SaldoAV': 0})
            dadosFim['AV_IND'] = dadosFim['SaldoAV'] + dadosFim['SaldoIND']
            dadosFim = dadosFim[['CODPROD', 'DESCRICAO', 'RUA', 'PREDIO', 'APTO', 'AV_DT','IND_DT', 'SaldoIND', 'SaldoAV', 'AV_IND']]
            dfFiltro = dadosFim.loc[dadosFim['AV_IND'] > 0]

            if retirarCol:
                dfFiltro = dfFiltro.drop(columns= retirarCol)

            self.PontoPartida = "AMBOS"
            return dfFiltro
        except Exception as e:
            self.validador.registrar_log(e, "Consolidado")
