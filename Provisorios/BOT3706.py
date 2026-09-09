from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ)),

from src.lib.settings import ColNames, OutPut, Wms, Relatorios
from src.lib import ValidarErros

import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="Workbook contains no default style")

from datetime import datetime,timedelta

import pyperclip as pc
import pyautogui as pag

import pandas as pd
import numpy as np
import time
import os


class auxiliar:
    @staticmethod
    def _copiar_e_validar(valor, tentativas=5):
        """Garante que o valor foi devidamente copiado para a área de transferência."""
        str_valor = str(valor)
        pc.copy(str_valor)
        for _ in range(tentativas):
            if pc.paste() == str_valor:
                return True
            pag.sleep(0.1)
            pc.copy(str_valor)
        return False

    @staticmethod
    def limpar_terminal() -> None:
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def ajuste_numeros(valor):
        """Converte colunas de texto formatadas em moeda/número pt-BR para float de forma performática."""
        if isinstance(valor, (int, float)):
            return float(valor) if pd.notna(valor) else 0.0
            
        val_str = str(valor).strip()
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
    @staticmethod
    def exibir_info_arquivos(paths: list[str]) -> None:
        """Exibe o cabeçalho padronizado com nome e data de modificação dos arquivos."""
        print("=" * 71)
        for caminho in paths:
            if os.path.exists(caminho):
                nome = os.path.basename(caminho)
                timestamp = os.path.getmtime(caminho)
                data_formatada = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
                print(f"[ARQUIVO]: {nome}\n"
                      f"[MODIFICADO EM]: {data_formatada}\n")
            else:
                print(f"[ALERTA]: Arquivo não encontrado -> {caminho}")
        print("=" * 71 + "\n")

class RetirarEndereco:
    validador = ValidarErros(fonte="Retirar_B06")
    def __init__(self, arquivo, largura):
        self.valvula = False
        self.largura = largura
        self.velocidade = 0.24

        lista_arquivos = [arquivo, Wms.endereco07]
        lista_saida = [OutPut.BotSave]
        self.ExecutarBot(list_extract= lista_arquivos, list_carga= lista_saida)

    def __simulador(self, dataFrame: pd.DataFrame):
        lista = []
        total_itens = len(dataFrame)
        inicio = time.perf_counter()

        for fase, (_,registro) in enumerate(dataFrame.iterrows(), 1):
            pag.sleep(self.velocidade)
            auxiliar._copiar_e_validar(registro['CODPROD'])
            pag.hotkey("ctrl", "v")
            
            pag.sleep(self.velocidade)
            pag.press("enter")
            pag.press("tab")
            pag.press("enter")

            for _ in range(7):
                pag.press("tab")
                pag.sleep(self.velocidade)

            pag.press("enter")
            pag.press("tab")

            for _ in range(2):
                pag.press("enter")
                pag.sleep(self.velocidade)

            pag.hotkey("shift", "tab")
            pag.press("enter")

            fim = time.perf_counter()
            tempo_segundos = fim - inicio
            print(
                f"\rProgresso: [{fase}/{total_itens}] - Itens restantes: {total_itens - fase} | {timedelta(seconds=int(tempo_segundos))}", 
                end="", flush=True)
            lista.append(fase)
        print()
        pass
    def __pipeline(self, list_extract: list[str], list_carga: list[str]):
        try:
            dataBase = pd.read_excel(list_extract[0], sheet_name= "Retirada")
            endereco = pd.read_csv(list_extract[1], header= None, names= ColNames.Endereco, dtype=str)
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return pd.DataFrame()
        try:
            Apartemantos = endereco.loc[endereco["TIPO_PK"] == "AP", ["COD", "TIPO_PK", "ENTRADA", "SAIDA", "DISP"]].copy()
            Apartemantos["CODPROD"] = pd.to_numeric(Apartemantos["COD"], errors="coerce").fillna(0).astype(int)

            for coluna in ["ENTRADA", "SAIDA", "DISP"]:
                Apartemantos[coluna] = Apartemantos[coluna].apply(auxiliar.ajuste_numeros)
            Apartemantos["MOVI"] = Apartemantos["ENTRADA"] + Apartemantos["SAIDA"]

            livres = (Apartemantos["DISP"] == 0) & (Apartemantos["MOVI"] == 0)
            pendencias = Apartemantos["MOVI"] > 0
            ocupados = Apartemantos["DISP"] > 0
            negativados = Apartemantos["DISP"] < 0

            Apartemantos["__CATEGORIAS__"] = np.select(
                [livres, pendencias, ocupados, negativados],
                ["Livre", "Pendente", "Ocupado", "Negativado"],
                default="Validar",
            )

            dataBase["CODPROD"] = pd.to_numeric(dataBase["CODPROD"], errors="coerce").fillna(0).astype(int)
            dataBase["DTULTENT"] = pd.to_datetime(dataBase["DTULTENT"], errors="coerce")

            dataConsolidado = dataBase.merge(Apartemantos, on="CODPROD", how='left').drop(columns=["COD", "TIPO_PK"])

            corte_livre = dataConsolidado.loc[
                (dataConsolidado["QTESTGER"] == 0)
                & (dataConsolidado["OBSFL"] == "FL")
                & (dataConsolidado["__CATEGORIAS__"] == "Livre")
            ]
            corte_resto = dataConsolidado.loc[~dataConsolidado["CODPROD"].isin(corte_livre["CODPROD"])]
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return pd.DataFrame()

        try:
            with pd.ExcelWriter(list_carga[0], engine='openpyxl') as save:
                corte_livre.to_excel(save, sheet_name="RETIRADA", index=False)
                corte_resto.to_excel(save, sheet_name="ValidarProd", index=False)
                self.valvula = True
            return corte_livre
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            raise

    def ExecutarBot(self, list_extract: list[str], list_carga: list[str]):
        auxiliar.limpar_terminal()
        auxiliar.exibir_info_arquivos(list_extract)

        produtos = self.__pipeline(list_extract= list_extract, list_carga= list_carga)
        if produtos.empty:
            print(">>Não foram encontrados produtos para transferência.")
            return

        quantidade = produtos['CODPROD'].nunique()
        print(f">>Quantidade de produtos a serem transferido: {quantidade}")
        input(">>Pressione [ENTER] para continuar...")
        auxiliar.limpar_terminal()

        print("\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n")
        for segundos in range(5, 0, -1):
            print(f"\r>>Iniciando disparos em {segundos}s... NÃO MEXA NO MOUSE OU TECLADO!", end="", flush=True)
            pag.sleep(1.0)

        print("\n\n[STATUS] Automação em andamento...")

        VAR = self.__simulador(dataFrame= produtos)
        if VAR == quantidade: 
            print("\n\n")
            print("=" * self.largura)
            print("[SUCESSO] O script finalizou as tentativas de processamento.")
            input("\n>>Pressione [ENTER] para fechar esta janela com segurança...")
            print("=" * self.largura)
        else:
            print("\n\n")
            print("=" * self.largura)
            print(f"[PARCIAL] O script finalizou as tentativas de processamento | {VAR} itens.")
            input("\n>>Pressione [ENTER] para fechar esta janela com segurança...")
            print("=" * self.largura)

        if self.valvula:
            resposta = input("\nArquivo gerado. Deseja abrir o relatório? (S/N): ").strip().upper()
            if resposta in ["S", "SIM"]:
                os.startfile(list_carga[0])
                print("Arquivo aberto com sucesso!")
    pass
class InserirEndereco:
    validador = ValidarErros(fonte="Inserir_B06")
    def __init__(self, arquivo= pd.DataFrame, largura= 70):
        self.valvula = False
        self.largura = largura
        self.velocidade = 0.24

        lista_arquivos = [arquivo,Relatorios._8596, Wms.endereco07]
        lista_saida = [OutPut.BotSave]

        self.ExecutarBot(listaPath= lista_arquivos, listaSave= lista_saida)
        pass

    def __Simulador(self, df: pd.DataFrame):
        try:
            lista = []
            total_itens = len(df)
            inicio = time.perf_counter()
            for fase, (_, registro) in enumerate(df.iterrows(), 1):
                pag.sleep( self.velocidade)

                # --- ETAPA 1: Inserir Código do Produto ---
                cod_prod = registro['CODPROD']
                if not auxiliar._copiar_e_validar(cod_prod):
                    print(f"\nErro ao copiar produto: {cod_prod}")
                    continue
                pag.hotkey("ctrl", "v")
                pag.press('enter')

                # --- ETAPA 2: Inserir Endereço ---
                pag.sleep( self.velocidade)
                destino = registro['DESTINO']
                if not auxiliar._copiar_e_validar(destino):
                    print(f"Erro ao copiar endereço: {destino}")
                    continue
                pag.hotkey("ctrl", "v")
                pag.press('enter')

                # --- ETAPA 3: Inserir Capacidade ---
                pag.sleep( self.velocidade)
                capacidade = registro['CAPACIDADE']
                if not auxiliar._copiar_e_validar(capacidade):
                    print(f"Erro ao copiar endereço: {capacidade}")
                    continue
                pag.hotkey("ctrl", "v")
                pag.press('enter')

                # --- ETAPA 4: Inserir Ponto de Reposiçõa ---
                pag.sleep( self.velocidade)
                ponto = registro['PONTO_REP']
                if not auxiliar._copiar_e_validar(ponto):
                    print(f"Erro ao copiar endereço: {ponto}")
                    continue
                pag.hotkey("ctrl", "v")
                pag.press('enter')

                # --- Finalizar e passar para o proximo
                pag.sleep( self.velocidade)
                pag.press('enter')
                pag.press('enter')
                
                # Sucesso do item atual
                fim = time.perf_counter()
                tempo_segundos = fim - inicio
                print(
                    f"\rProgresso: [{fase}/{total_itens}] - Itens restantes: {total_itens - fase} | {timedelta(seconds=int(tempo_segundos))}", 
                    end="", flush=True)
                lista.append(fase)

            return len(lista)
        except Exception as e:
            print()
            ValidarErros(e, etapa="simulador")

        pass
    def __pipeline(self, listaPath: list[str], listaSave: list[str]):
        try:
            base = pd.read_excel(listaPath[0], sheet_name= 'adiconarPK')
            dataProd = pd.read_excel(listaPath[1], usecols= ['CODPROD'])
            dataEnd = pd.read_csv(listaPath[2], header= None, usecols=[0])
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return pd.DataFrame()
        try:
            comEnd = base['CODPROD'].isin(dataProd['CODPROD'])
            comProd = base['DESTINO'].isin(dataEnd[0])

            base["ANALISE"] =np.select([comEnd, comProd], ["PROD_COM_END", "END_COM_PROD"], default= "CORRETO")

            processado = base.loc[base["ANALISE"]== 'CORRETO'].copy()
            paraTratar = base.loc[base["ANALISE"]!= 'CORRETO'].copy()
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return pd.DataFrame()
        try:
            with pd.ExcelWriter(listaSave[0], engine= 'openpyxl') as var:
                paraTratar.to_excel(var, sheet_name= "ParaTratar", index= False)
                processado.to_excel(var, sheet_name= 'Processado', index= False)
                self.valvula = True
            
            return processado
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return pd.DataFrame()

    def ExecutarBot(self, listaPath: list[str], listaSave: list[str]):
        auxiliar.limpar_terminal()
        auxiliar.exibir_info_arquivos(listaPath)
        input("Pressione [ENTER] para continuar...")

        produtos = self.__pipeline(listaPath= listaPath, listaSave= listaSave)

        if produtos.empty:
            print("Não foram encontrados produtos para transferência.")
            if self.valvula:
                resposta = input("\nArquivo gerado. Deseja abrir o relatório? (S/N): ").strip().upper()
                if resposta in ["S", "SIM"]:
                    os.startfile(listaSave[0])
                    print("Arquivo aberto com sucesso!")
            else:
                print("Nenhum arquivo gerado.")
            input("Pressione [ENTER] para continuar...")
            return

        qtde = produtos['CODPROD'].nunique()
        print(f"Quantidade de produtos a serem transferido: {qtde}")
        input("Pressione [ENTER] para continuar...")
        auxiliar.limpar_terminal()
        
        print("\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n")
        for segundos in range(5, 0, -1):
            print(f"\rIniciando disparos em {segundos}s... NÃO MEXA NO MOUSE OU TECLADO!", end="", flush=True)
            pag.sleep(1.0)

        print("\n\n[STATUS] Automação em andamento...")

        VAR = self.__Simulador(df= produtos)
        if VAR == qtde: 
            print("\n\n")
            print("=" * self.largura)
            print("[SUCESSO] O script finalizou as tentativas de processamento.")
            input("\nPressione [ENTER] para fechar esta janela com segurança...")
            print("=" * self.largura)
        else:
            print("\n\n")
            print("=" * self.largura)
            print(f"[PARCIAL] O script finalizou as tentativas de processamento | {VAR} itens.")
            input("\nPressione [ENTER] para fechar esta janela com segurança...")
            print("=" * self.largura)

        if self.valvula:
            resposta = input("\nArquivo gerado. Deseja abrir o relatório? (S/N): ").strip().upper()
            if resposta in ["S", "SIM"]:
                os.startfile(listaSave[0])
                print("Arquivo aberto com sucesso!")
class ProcessarCapacidade:
    validador = ValidarErros(fonte="Capacidade_B06")
    def __init__(self, largura):
        self.largura = largura
        listaArquivos = [OutPut.Cadastro, Wms.endereco07]
        self.velocidade = 0.24

        self.ExecutarBot(listaArquivos)
        pass

    def __Simulador(self, DataFrame: pd.DataFrame, coluna: str):
        print()
        total = DataFrame['CODPROD'].nunique()
        listaTransf = []
        for fase, (indice, registro) in enumerate(DataFrame.iterrows(), 1):

            pag.sleep( self.velocidade)
            cod_prod = registro['CODPROD']
            if not auxiliar._copiar_e_validar(cod_prod):
                print(f"\nErro ao copiar produto: {cod_prod}")
                continue
            pag.hotkey("ctrl", "v")

            pag.press("enter")
            pag.press("tab")
            pag.press("enter")

            pag.sleep( self.velocidade)
            col_cap = registro[coluna]
            if not auxiliar._copiar_e_validar(col_cap):
                print(f"\nErro ao copiar produto: {col_cap}")
            pag.hotkey("ctrl", "v")

            pag.press("enter")

            pag.sleep( self.velocidade)
            pontinho = registro["PONTO"]
            if not auxiliar._copiar_e_validar(pontinho):
                print(f"\nErro ao copiar produto: {pontinho}")
            pag.hotkey("ctrl", "v")

            pag.press("enter")
            pag.press("enter")

            print(f"\rProgresso: [{fase}/{total}] - Itens restantes: {total - fase} ", end="", flush=True)
            listaTransf.append(registro["CODPROD"])
        return listaTransf
    def __pipeline(self, listaPath: list[str]):
        try:
            colunas_necessarias = ["CODPROD", "PL_LASTRO", "PL", "CAP", "QTEnd", "V_CAP"]
            cadastroDIV = pd.read_excel(listaPath[0],usecols= colunas_necessarias, sheet_name="cadastro")
            enderecado = pd.read_csv(listaPath[1], header=None, names=ColNames.Endereco, dtype=str)
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            Apartamentos = enderecado[["COD", "ENTRADA", "SAIDA", "DISP"]].loc[enderecado['TIPO_PK'] == 'AP'].copy()
            for valor in ["DISP", "ENTRADA", "SAIDA"]:
                Apartamentos[valor] = Apartamentos[valor].apply(auxiliar.ajuste_numeros)

            Apartamentos["PENDENTE"] = Apartamentos["ENTRADA"] + Apartamentos["SAIDA"]
            vazio = (Apartamentos["DISP"] == 0) & (Apartamentos["PENDENTE"] == 0)
            ocupado = (Apartamentos["DISP"] > 0) & (Apartamentos["PENDENTE"] == 0)
            pendente = Apartamentos["PENDENTE"] > 0
            negativos = Apartamentos["DISP"] < 0

            Apartamentos["CATEGORIA"] = np.select([vazio, ocupado, pendente, negativos], ["VAZIO", "OCUPADO", "PENDENCIA","NEGATIVO"], default="Anomalia")
            Apartamentos["COD"] = pd.to_numeric(Apartamentos['COD'], errors= 'raise').astype(int)
            Apartamentos = Apartamentos.rename(columns= {"COD":"CODPROD"})

            consolidado = cadastroDIV.merge(Apartamentos, on="CODPROD", how="left")
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            filtragem = consolidado.loc[(consolidado['QTEnd'] == 2) & (consolidado['V_CAP'] != "NORMAL")].copy()
            dataUP = filtragem.loc[(filtragem["V_CAP"] == "DIV_UP")].copy()
            dataUP["PONTO"] = (dataUP["PL"] * 0.3).round(0).astype(int)
            dataUP = dataUP[["CODPROD", "PL", "PONTO", "CATEGORIA", "V_CAP"]].drop_duplicates(subset=["CODPROD"], keep="first")

            dataDOWN = filtragem.loc[(filtragem["V_CAP"] == "DIV_DOWN")].copy()
            dataDOWN["PONTO"] = (dataDOWN["PL_LASTRO"] * 0.3).round(0).astype(int)
            dataDOWN = dataDOWN[["CODPROD", "PL_LASTRO", "PONTO", "CATEGORIA", "V_CAP"]].drop_duplicates(subset=["CODPROD"], keep="first")
            return dataUP, dataDOWN
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False

    def ExecutarBot(self, listaPath: list[str]):
        auxiliar.limpar_terminal()
        auxiliar.exibir_info_arquivos(listaPath)

        dataUP, dataDOWN = self.__pipeline(listaPath= listaPath)
        print(f">> Encontrados no dataUP: {dataUP['CODPROD'].nunique()} item(s)")
        print(f">> Encontrados no dataDOWN:  {dataDOWN['CODPROD'].nunique()} item(s)\n")

        print(" SELEÇÃO DE MODALIDADE ".center(self.largura, "="))
        print(" 1 - 'dataUP' (Usará PL) | 2 - 'dataDOWN' (Usará PL_LASTRO)")

        while True:
            escolha = int(input("Digite a opção desejada (1 ou 2): ").strip())
            if escolha == 1:
                capacidade = "PL"
                dataMod = dataUP.copy()
                break
            elif escolha == 2:
                capacidade = "PL_LASTRO"
                dataMod = dataDOWN.copy()
                break
            else:
                print("[ALERTA] Opção inválida! Digite estritamente 1 ou 2.")

        auxiliar.limpar_terminal()
        print("=" * self.largura)
        print(f">> TOTAL DE REGISTROS A PROCESSAR: {len(dataMod)}")
        print("=" * self.largura)

        input("\n>> Prepare a tela do sistema e pressione [ENTER] para continuar...")
        print("\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n")

        for segundos in range(5, 0, -1):
            print(f"\r>> Iniciando disparos em {segundos}s... NÃO MEXA NO MOUSE OU TECLADO!", end="", flush=True)
            pag.sleep(1.0)

        auxiliar.limpar_terminal()
        print("CAPADIDADE AUTOBOT")
        print("\n\n[STATUS] Automação em andamento...")

        print(type(dataMod))
        retorno = self.__Simulador(dataMod, capacidade)
        if retorno:
            print(">> Transferencia finalizada...")
        pass

