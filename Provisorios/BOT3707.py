from pathlib import Path
import sys
RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))

from src.lib.settings import ColNames, OutPut, Wms
from src.lib import ValidarErros

import pyautogui as pag
import pyperclip as pc

from datetime import datetime
import pandas as pd
import numpy as np
import os

class auxiliar:
    def limpar_terminal() -> None:
        os.system("cls" if os.name == "nt" else "clear")

        pass
    def ajuste_numeros(df: pd.DataFrame, colunas: list[str]):
        """Converte colunas de texto formatadas em moeda/número pt-BR para float de forma performática."""
        for col in colunas:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(-1).astype(float)
        return df
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
    def exibir_info_arquivos(paths: list[str]) -> None:
        """Exibe o cabeçalho padronizado com nome e data de modificação dos arquivos."""
        print("=" * 60)
        for caminho in paths:
            if os.path.exists(caminho):
                nome = os.path.basename(caminho)
                timestamp = os.path.getmtime(caminho)
                data_formatada = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
                print(f"[ARQUIVO]: {nome}\n"
                      f"[MODIFICADO EM]: {data_formatada}\n")
            else:
                print(f"[ALERTA]: Arquivo não encontrado -> {caminho}")
        print("=" * 60 + "\n")

class TransferirPROD:
    validador = ValidarErros(fonte="ContagemINV")
    def __init__(self, arquivo):
        self.largura = 71
        self.valvula_salva = False
        self.velocidade = 0.3

        lista_arquivos = [arquivo, Wms.endereco07]
        lista_saida = [OutPut.BotSave]
        auxiliar.limpar_terminal()
        auxiliar.exibir_info_arquivos(lista_arquivos)
        input("Pressione [ENTER] para continuar...")
        self.ExecutarBot(listaPath= lista_arquivos, listaSave= lista_saida)

    def __Simulador(self, df: pd.DataFrame):
        try:
            lista = []
            total_itens = len(df)
            for fase, (_, registro) in enumerate(df.iterrows(), 1):

                # --- ETAPA 1: Inserir Código do Produto ---
                cod_prod = registro['CODPROD']
                if not auxiliar._copiar_e_validar(cod_prod):
                    print(f"\nErro ao copiar produto: {cod_prod}")
                    continue
                pag.sleep( self.velocidade)
                pag.hotkey("ctrl", "v")
                pag.sleep( self.velocidade)
                pag.press('enter')

                # --- ETAPA 2: Inserir Endereço ---
                destino = registro['DESTINO']
                if not auxiliar._copiar_e_validar(destino):
                    print(f"Erro ao copiar endereço: {destino}")
                    continue
                pag.sleep( self.velocidade)
                pag.hotkey("ctrl", "v")
                pag.sleep( self.velocidade)

                for _ in range(3):
                    pag.sleep( self.velocidade)
                    pag.press('enter')

                # Sucesso do item atual
                print(f"\rProgresso: [{fase}/{total_itens}] - Itens restantes: {total_itens - fase} ", end="", flush=True)
                lista.append(fase)
            return len(lista)
        except Exception as e:
            ValidarErros(e, etapa="simulador")
    def __pipeline(self, listaPath, listaSave):
        try:
            base_dados = pd.read_excel(listaPath[0], sheet_name= 'transf3707')
            endereco = pd.read_csv(listaPath[1], header=None, names=ColNames.Endereco, dtype=str)
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False  
        try:
            end = endereco.query("TIPO_PK == 'AP'")[["COD_END", "COD", "TIPO_PK", "ENTRADA", "SAIDA", "DISP"]].copy()
            end = auxiliar.ajuste_numeros(end, ["ENTRADA", "SAIDA", "DISP"])
            end["MOVI"] = end["ENTRADA"] + end["SAIDA"]

            livre = (end["DISP"] == 0) & (end["MOVI"] == 0)
            pendencias = end["MOVI"] > 0
            ocupado = end["DISP"] > 0
            negativado = end["DISP"] < 0

            end["CATEG_PROD"] = np.select(
                [livre, pendencias, ocupado, negativado],
                ["Livre", "Pendente", "Ocupado", "Negativado"],
                default="Validar",
            )
            base_dados["CODPROD"] = pd.to_numeric(base_dados["CODPROD"], errors="coerce").fillna(0).astype(int)
            end["CODPROD"] = pd.to_numeric(end["COD"], errors="coerce").fillna(0).astype(int)
            base_dados["DESTINO"] = pd.to_numeric(base_dados["DESTINO"], errors="coerce").fillna(0).astype(int)
            corte = end[['COD_END']]
            corte["CATEG_PK"] = pd.to_numeric(corte["COD_END"], errors="coerce").fillna(0).astype(int)
            corte = corte.drop(columns= 'COD_END')

            Produtos = base_dados.merge(end, on= 'CODPROD', how= 'left').drop(columns= 'COD')
            Produtos = Produtos.merge(corte, left_on= "DESTINO", right_on= "CATEG_PK", how= "left")

            Produtos['CATEG_PK'] = np.where(Produtos['CATEG_PK'].notna(), "Ocupado", "Livre")

            dfProntos = Produtos.query("CATEG_PROD in ['Livre', 'Ocupado'] and CATEG_PK == 'Livre'").copy()
            dfPendentes = Produtos.drop(dfProntos.index).copy()
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:

            with pd.ExcelWriter(listaSave[0], engine= 'openpyxl') as var:
                dfProntos.to_excel(var, sheet_name= "Transferidos", index= False)
                dfPendentes.to_excel(var, sheet_name= "Pendencias", index= False)
                self.valvula_salva = True
            return dfProntos
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False

    def ExecutarBot(self,listaPath, listaSave):
        auxiliar.limpar_terminal()
        produtos = self.__pipeline(listaPath=listaPath, listaSave= listaSave)

        if produtos.empty:
            print("Não foram encontrados produtos para transferência.")
            if self.valvula_salva:
                resposta = input("\nArquivo gerado. Deseja abrir o relatório? (S/N): ").strip().upper()
                if resposta in ["S", "SIM"]:
                    os.startfile(OutPut.Jupyter_1)
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

        print(type(produtos))
        print(produtos.head(3))
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

        if self.valvula_salva:
            resposta = input("\nArquivo gerado. Deseja abrir o relatório? (S/N): ").strip().upper()
            if resposta in ["S", "SIM"]:
                os.startfile(OutPut.Jupyter_1)
                print("Arquivo aberto com sucesso!")
        pass
