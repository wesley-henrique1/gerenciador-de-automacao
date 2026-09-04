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
    def __init__(self, arquivo):
        lista_arquivos = [arquivo, Wms.endereco07]
        self.valvula_salva = False
        auxiliar.limpar_terminal()
        auxiliar.exibir_info_arquivos(lista_arquivos)
        input("Pressione [ENTER] para continuar...")
        self.executar_automacao(lista_arquivos)

    def _pipeline(self, lista_path: list[str]):

        base_dados = pd.read_excel(lista_path[0], sheet_name="Retirada")
        if base_dados.empty:
            print("A aba 'Retirada' está vazia ou sem registros.")
            return
        endereco = pd.read_csv(lista_path[1], header=None, names=ColNames.Endereco, dtype=str)

        end = endereco.loc[endereco["TIPO_PK"] == "AP", ["COD", "TIPO_PK", "ENTRADA", "SAIDA", "DISP"]].copy()
        for valor in ["ENTRADA", "SAIDA", "DISP"]:
                end[valor] = end[valor].apply(auxiliar.ajuste_numeros)

        end["MOVI"] = end["ENTRADA"] + end["SAIDA"]

        livre = (end["DISP"] == 0) & (end["MOVI"] == 0)
        pendencias = end["MOVI"] > 0
        ocupado = end["DISP"] > 0
        negativado = end["DISP"] < 0

        end["CATEGORIAS"] = np.select(
            [livre, pendencias, ocupado, negativado],
            ["Livre", "Pendente", "Ocupado", "Negativado"],
            default="Validar",
        )
        base_dados["CODPROD"] = pd.to_numeric(base_dados["CODPROD"], errors="coerce").fillna(0).astype(int)
        end["CODPROD"] = pd.to_numeric(end["COD"], errors="coerce").fillna(0).astype(int)

        base_dados["DTULTENT"] = pd.to_datetime(base_dados["DTULTENT"], errors="coerce")

        base = base_dados.merge(end, on="CODPROD", how='left').drop(columns=["COD", "TIPO_PK"])
        corte_livre = base.loc[
            (base["QTESTGER"] == 0)
            & (base["OBSFL"] == "FL")
            & (base["CATEGORIAS"] == "Livre")
        ]

        corte_resto = base.loc[~base["CODPROD"].isin(corte_livre["CODPROD"])]
        codigos = corte_livre["CODPROD"].drop_duplicates().tolist()
        try:
            with pd.ExcelWriter(OutPut.Jupyter_1) as save:
                corte_livre.to_excel(save, sheet_name="RETIRADA", index=False)
                corte_resto.to_excel(save, sheet_name="ValidarProd", index=False)
                self.valvula_salva = True
        except PermissionError:
            print(f"\n[ERRO DE PERMISSÃO] Feche o arquivo '{OutPut.Jupyter_1}' no Excel antes de continuar!")
            self.valvula_salva = False

        return codigos
    def executar_automacao(self, lista_path: list[str]):
        dados = self._pipeline(lista_path)
        if dados:
            print(f"\nQuantidade de Produtos a serem processado: {len(dados)}\n")
        input("Pressione [ENTER] para continuar...")

        auxiliar.limpar_terminal()
        trava = 0.2

        if dados:
            print("\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n")
            for segundos in range(5, 0, -1):
                print(f"\rIniciando disparos em {segundos}s... NÃO MEXA NO MOUSE OU TECLADO!", end="", flush=True)
                pag.sleep(1.0)

            print("\n\n[STATUS] Automação em andamento...")
            total = len(dados)

            for fase, registro in enumerate(dados, 1):
                auxiliar.verificar_copy(registro)
                
                # Sequência de atalhos e navegação
                pag.press("enter")
                pag.sleep(trava)
                pag.press("tab")
                pag.sleep(trava)
                pag.press("enter")
                pag.sleep(trava)

                # Avançar 7 campos
                for _ in range(7):
                    pag.press("tab")
                    pag.sleep(trava)

                pag.press("enter")
                pag.sleep(trava)
                pag.press("tab")
                pag.sleep(trava)

                # Confirmar acões
                for _ in range(2):
                    pag.press("enter")
                    pag.sleep(trava)

                pag.hotkey("shift", "tab")
                pag.sleep(trava)
                pag.press("enter")
                pag.sleep(trava)

                print(f"\rProgresso: [{fase}/{total}] - Itens restantes: {total - fase} ", end="", flush=True)
            print("\n\n[SUCESSO] Processo de retirada finalizado!")
        else:
            print("[AVISO] Nenhum registro válido encontrado para esta modalidade.")

        if self.valvula_salva:
            resposta = input("\nArquivo gerado. Deseja abrir o relatório? (S/N): ").strip().upper()
            if resposta in ["S", "SIM"]:
                os.startfile(OutPut.Jupyter_1)
                print("Arquivo aberto com sucesso!")
class InserirEndereco:
    validador = ValidarErros(fonte="Inserir3606")
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
    def __init__(self, largura):
        self.largura = largura
        listaArquivos = [OutPut.Cadastro, Wms.endereco07]
        self.velocidade = 0.4

        self.ExecutarBot(listaArquivos)
        pass

    def __Simulador(self, DataFrame: pd.DataFrame, coluna: str):
        print()
        total = DataFrame['CODPROD'].nunique()
        listaTransf = []
        for fase, (indice, registro) in enumerate(DataFrame.iterrows(), 1):
            pag.sleep( self.velocidade)
            auxiliar.verificar_copy(registro["CODPROD"])
            pag.press("enter")
            pag.sleep( self.velocidade)

            pag.press("tab")
            pag.sleep( self.velocidade)
            pag.press("enter")

            auxiliar.verificar_copy(registro[coluna])
            pag.press("enter")
            pag.sleep( self.velocidade)

            auxiliar.verificar_copy(registro["PONTO"])
            pag.press("enter")
            pag.sleep( self.velocidade)

            pag.press("enter")
            pag.sleep( self.velocidade)

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

