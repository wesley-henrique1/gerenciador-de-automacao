import pyautogui as pag
import pyperclip as pc
from datetime import datetime
from src.lib.settings import Wms, ColNames
import numpy as np
import pandas as pd
import os

class RetirarEndereco:
    def __init__(self):
        path = r'z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.6 - PCL Cadastro\Wesley Henrique\Produtos sem endereços.xlsx'
        listaArquivos = [path, Wms.endereco07]

        self.automact(listaArquivos)
        pass

    def __Verificarcopy(valor):
        tentativas_prod = 0
        pc.copy(str(valor))
        pag.sleep(0.02)
        while pc.paste() != str(valor) and tentativas_prod < 5:
            pag.sleep(0.1)
            pc.copy(str(valor))
            tentativas_prod += 1

        pag.hotkey("ctrl", "v")
        pass
    def __AjusteNumeros(self, DataFrame, colunas):
        for col in colunas:
            DataFrame[col] = DataFrame['DISP'].astype(str).str.replace('.', '').str.replace(',', '.')
            DataFrame[col] = pd.to_numeric(DataFrame[col], errors= 'coerce').fillna(-1).astype(float)
        return DataFrame
    def __limpar_terminal(self):
       return os.system("cls" if os.name == "nt" else "clear")


    def __pipeline(self, listaPath):
        for Arquivo in listaPath:
            NomeArquivo = os.path.basename(Arquivo)
            dataArquivo =os.path.getmtime(Arquivo)
            data_formatada = datetime.fromtimestamp(dataArquivo)

            dataArquivo = data_formatada.strftime("%d/%m/%Y %H:%M:%S")
            print(f"Arquivo: {NomeArquivo} | Modificado em: {dataArquivo}")
            pass
        BaseFora = pd.read_excel(listaPath[0])
        endereco = pd.read_csv(listaPath[1], header= None, names=ColNames.Endereco, dtype=str)

        try:
            endereco = self.__AjusteNumeros(endereco, ['COD','DISP', 'ENTRADA', 'SAIDA'])
            endereco['PENDENCIA'] = endereco['SAIDA'] + endereco['ENTRADA']
            apartementos = endereco.loc[endereco['TIPO_PK'] == 'AP'].copy()
            apartementos = apartementos[['COD', 'TIPO_PK','DISP','PENDENCIA']]
            apartementos['COD'] = apartementos['COD'].astype(int)

            BaseDados = BaseFora.merge(apartementos, left_on= 'CODPROD', right_on= 'COD', how= 'left').drop(columns= ['COD'])

            livre = (BaseDados['DISP'] == 0) & (BaseDados['PENDENCIA'] == 0)
            ocupado = (BaseDados['DISP'] != 0) & (BaseDados['PENDENCIA'] != 0)
            pendente = (BaseDados['PENDENCIA'] > 0)
            BaseDados['CATEGORIA'] = np.select([livre, ocupado, pendente], ['Livre', 'Ocupado', 'Pendente'], default= 'Verificar')


            QtdeVazio = BaseDados['CODPROD'].loc[BaseDados['CATEGORIA'] == 'Livre'].nunique()
            QtdeOcupado = BaseDados['CODPROD'].loc[BaseDados['CATEGORIA'] == 'Ocupado'].nunique()
            QtdePendente = BaseDados['CODPROD'].loc[BaseDados['CATEGORIA'] == 'Pendente'].nunique()

            print(f"Validação Produtos:")            
            print(f"Livre: {QtdeVazio} | Ocupado: {QtdeOcupado} | Pendente: {QtdePendente}")
            codigos = BaseDados['CODPROD'].copy()
            codigos = list(codigos.drop_duplicates())
            print(f"Quantidade de produtos a serem processados: {len(codigos)}")            
        except Exception as e:
            print(f"Erro na etapa de tratamento, {e}")
            codigos = 0
        
        return codigos

    def automact(self, lista):
        dados = self.__pipeline(lista)
        input("Apente [enter] para continuar")

        print('\n')

        self.__limpar_terminal()
        
        trava = 0.4
        if dados:
            print("\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n")            
            
            for segundos_restantes in range(5, 0, -1):    
                print(f"\rIniciando disparos em {segundos_restantes}s... NÃO MEXA NO MOUSE OU TECLADO!", end="", flush=True)          
                pag.sleep(1.0)

            print("\n\n[STATUS] Automação em andamento...")
            total = len(dados)
            for fase, registro in enumerate(dados, 1):           
                # Campo 1: Código do Produto
                self.__Verificarcopy(registro)
                pag.press('enter')
                pag.sleep(trava)
                
                pag.hotkey("shift", "tab")
                pag.sleep(trava)

                pag.press('enter')
                pag.sleep(trava)

                pag.press("tab")
                pag.sleep(trava)

                for ws in range(2):
                    pag.press('enter')
                    pag.sleep(trava)

                pag.hotkey("shift", "tab")
                pag.sleep(trava)

                pag.press("tab")
                pag.sleep(trava)

                print(f"\rProgresso: [{fase}/{total}] - Itens restantes: {total - fase} ", end="", flush=True)
        else:
            print("[AVISO] Nenhum registro válido encontrado para esta modalidade.")

        pass

if __name__ == '__main__':
    RetirarEndereco()