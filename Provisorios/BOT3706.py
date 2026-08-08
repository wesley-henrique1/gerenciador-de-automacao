from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))
from src.lib.settings import ColNames, OutPut, Wms

import os
from datetime import datetime
import numpy as np
import pandas as pd
import pyautogui as pag
import pyperclip as pc


class auxiliar:
    @staticmethod
    def verificar_copy(valor: str | int | float, tentativas: int = 5) -> None:
        """Copia o valor para o clipboard garantindo que o buffer do SO seja atualizado antes de colar."""
        valor_str = str(valor)
        pc.copy(valor_str)
        pag.sleep(0.02)
        count = 0
        while pc.paste() != valor_str and count < tentativas:
            pag.sleep(0.05)
            pc.copy(valor_str)
            count += 1
        pag.hotkey("ctrl", "v")

    @staticmethod
    def limpar_terminal() -> None:
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def ajuste_numeros(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
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

    @staticmethod
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

class RetirarEndereco:
    def __init__(self, arquivo):
        lista_arquivos = [arquivo, Wms.endereco07]
        self.valvula_salva = False
        self.executar_automacao(lista_arquivos)

    def _pipeline(self, lista_path: list[str]):
        auxiliar.exibir_info_arquivos(lista_path)

        base_dados = pd.read_excel(lista_path[0], sheet_name="Retirada")
        if base_dados.empty:
            print("A aba 'Retirada' está vazia ou sem registros.")
            return
        endereco = pd.read_csv(lista_path[1], header=None, names=ColNames.Endereco, dtype=str)

        end = endereco.loc[endereco["TIPO_PK"] == "AP", ["COD", "TIPO_PK", "ENTRADA", "SAIDA", "DISP"]].copy()
        end = auxiliar.ajuste_numeros(end, ["ENTRADA", "SAIDA", "DISP"])
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
        print(corte_resto)
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
        auxiliar.limpar_terminal()
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
class Capacidade:
    def __init__(self):
        auxiliar.limpar_terminal()
        self.colunas_necessarias = ["CODPROD", "PL_LASTRO", "PL", "CAP", "QTEnd", "V_CAP"]
        self.valvula_execucao = False
        self.executar()

    @staticmethod
    def _disparar_teclas(lista_prod: list[dict], campo_capacidade: str) -> None:
        trava = 0.1
        total = len(lista_prod)

        for fase, registro in enumerate(lista_prod, 1):
            auxiliar.verificar_copy(registro["CODPROD"])
            pag.press("enter")
            pag.sleep(trava)

            pag.press("tab")
            pag.sleep(trava)
            pag.press("enter")

            auxiliar.verificar_copy(registro[campo_capacidade])
            pag.press("enter")
            pag.sleep(trava)

            auxiliar.verificar_copy(registro["PONTO"])
            pag.press("enter")
            pag.sleep(trava)

            pag.press("enter")
            pag.sleep(trava)

            print(f"\rProgresso: [{fase}/{total}] - Itens restantes: {total - fase} ", end="", flush=True)

    def pipeline(self) -> tuple[str, list[dict]]:
        try:
            dados = pd.read_excel(OutPut.Cadastro, usecols=self.colunas_necessarias, sheet_name="cadastro")
            enderecado = pd.read_csv(Wms.endereco07, header=None, names=ColNames.Endereco, dtype=str)

            end = enderecado[["DISP", "COD", "ENTRADA", "SAIDA"]].copy()
            end = auxiliar.ajuste_numeros(end, ["DISP", "ENTRADA", "SAIDA"])

            end["PENDENTE"] = end["ENTRADA"] + end["SAIDA"]
            vazio = (end["DISP"] == 0) & (end["PENDENTE"] == 0)
            ocupado = (end["DISP"] > 0) & (end["PENDENTE"] == 0)
            pendente = end["PENDENTE"] > 0

            end["CATEGORIA"] = np.select([vazio, ocupado, pendente], ["VAZIO", "OCUPADO", "PENDENCIA"], default="Anomalia")

            dados = dados.merge(end, left_on="CODPROD", right_on="COD", how="left")

            auxiliar.exibir_info_arquivos([OutPut.Cadastro, Wms.endereco07])

            # Filtros UP e DOWN
            filtro_base = (dados["QTEnd"] == 2) & (dados["CATEGORIA"] != "PENDENCIA")
            
            df_up = dados.loc[(dados["V_CAP"] == "DIV_UP") & filtro_base].copy()
            df_up["PONTO"] = (df_up["PL"] * 0.3).round(0).astype(int)
            df_up = df_up.drop_duplicates(subset=["CODPROD"], keep="first")
            lista_up = df_up[["CODPROD", "PL", "PONTO", "CATEGORIA", "V_CAP"]].to_dict(orient="records")

            df_down = dados.loc[(dados["V_CAP"] == "DIV_DOWN") & filtro_base].copy()
            df_down["PONTO"] = (df_down["PL_LASTRO"] * 0.3).round(0).astype(int)
            df_down = df_down.drop_duplicates(subset=["CODPROD"], keep="first")
            lista_down = df_down[["CODPROD", "PL_LASTRO", "PONTO", "CATEGORIA", "V_CAP"]].to_dict(orient="records")

            print(f">> Encontrados no DF_UP: {len(lista_up)} item(s)")
            print(f">> Encontrados no DF_DOWN: {len(lista_down)} item(s)")
            print("=" * 19 + " SELEÇÃO DE MODALIDADE " + "=" * 19)
            print(" 1 - 'DF_UP' (Usará PL) | 2 - 'DF_DOWN' (Usará PL_LASTRO)")
            print("-" * 61)

            while True:
                escolha = input("Digite a opção desejada (1 ou 2): ").strip()
                if escolha == "1":
                    capacidade = "PL"
                    lista_mod = lista_up
                    break
                elif escolha == "2":
                    capacidade = "PL_LASTRO"
                    lista_mod = lista_down
                    break
                else:
                    print("[ALERTA] Opção inválida! Digite estritamente 1 ou 2.")

            self.valvula_execucao = True
            return capacidade, lista_mod

        except Exception as e:
            print(f"\n[ERRO CRÍTICO] Houve uma falha no processamento de dados: {e}")
            self.valvula_execucao = False
            return "", []

    def executar(self) -> None:
        try:
            capacidade, lista_mod = self.pipeline()
            if not self.valvula_execucao or not lista_mod:
                print("\n[AVISO] Nenhuma ação a ser realizada ou nenhum registro encontrado.")
                input("Pressione [ENTER] para voltar ao menu...")
                return

            auxiliar.limpar_terminal()
            print("=" * 60)
            print(f">> TOTAL DE REGISTROS A PROCESSAR: {len(lista_mod)}")
            print("=" * 60 + "\n")

            input(">> Prepare a tela do sistema e pressione [ENTER] para continuar...")
            print("\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n")

            for segundos in range(5, 0, -1):
                print(f"\rIniciando disparos em {segundos}s... NÃO MEXA NO MOUSE OU TECLADO!", end="", flush=True)
                pag.sleep(1.0)

            print("\n\n[STATUS] Automação em andamento...")
            self._disparar_teclas(lista_prod=lista_mod, campo_capacidade=capacidade)

        except Exception as e:
            print(f"\n\n[ERRO] Falha durante a execução da automação: {e}")

        print("\n\n" + "=" * 60)
        print("[SUCESSO] O script finalizou as tentativas de processamento.")
        print("=" * 60)
        input("\nPressione [ENTER] para fechar esta janela com segurança...")


