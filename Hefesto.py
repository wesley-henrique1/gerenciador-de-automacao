import os
import time
from datetime import datetime
import numpy as np
import pandas as pd
import pyautogui as pag
import pyperclip as pc
from src.lib.settings import ColNames, OutPut, Wms


class Aux:

    @staticmethod
    def verificarcopy(valor):
        tentativas_prod = 0
        pc.copy(str(valor))
        pag.sleep(0.02)
        while pc.paste() != str(valor) and tentativas_prod < 5:
            pag.sleep(0.1)
            pc.copy(str(valor))
            tentativas_prod += 1

        pag.hotkey("ctrl", "v")

    @staticmethod
    def limpar_terminal():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def ajuste_numeros(data_frame, colunas):
        for col in colunas:
            data_frame[col] = (
                data_frame[col]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            data_frame[col] = (
                pd.to_numeric(data_frame[col], errors="coerce")
                .fillna(-1)
                .astype(float)
            )
        return data_frame

class RetirarEndereco:
    def __init__(self):
        path = r"z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.6 - PCL Cadastro\Wesley Henrique\Produtos sem endereços.xlsx"
        listaArquivos = [path, Wms.endereco07]
        self.ValvulaSave = False
        self.automact(listaArquivos)

    def __pipeline(self, listaPath):
        for Arquivo in listaPath:
            NomeArquivo = os.path.basename(Arquivo)
            dataArquivo = os.path.getmtime(Arquivo)
            data_formatada = datetime.fromtimestamp(dataArquivo).strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            print(f"Arquivo: {NomeArquivo} | Modificado em: {data_formatada}")

        baseDados = pd.read_excel(listaPath[0], sheet_name="Stage")
        endereco = pd.read_csv(
            listaPath[1], header=None, names=ColNames.Endereco, dtype=str
        )

        end = endereco[["COD", "TIPO_PK", "ENTRADA", "SAIDA", "DISP"]].copy()
        end = end.loc[(end["TIPO_PK"] == "AP")]
        end = Aux.ajuste_numeros(end, ["ENTRADA", "SAIDA", "DISP"])
        end["MOVI"] = end["ENTRADA"] + end["SAIDA"]

        livre = (end["DISP"] == 0) & (end["MOVI"] == 0)
        pedencias = end["MOVI"] > 0
        ocupado = end["DISP"] > 0
        negativado = end["DISP"] < 0
        end["CATEGORIAS"] = np.select(
            [livre, pedencias, ocupado, negativado],
            ["Livre", "Pedencia", "Ocupado", "negativado"],
            default="validar",
        )

        baseDados["CODPROD"] = baseDados["CODPROD"].astype(int)
        end["CODPROD"] = end["COD"].astype(int)

        baseDados['DTULTENT'] = pd.to_datetime(baseDados['DTULTENT'], errors= 'coerce')
        baseDados['SUPDT'] =  np.where(
            (datetime.now() - baseDados['DTULTENT'] ).dt.days > 30,
            "sup", "inf"
        )
        base = baseDados.merge(end, on="CODPROD", how="inner").drop(
            columns=["COD", "TIPO_PK"]
        )

        DfCompleto = base.loc[
            (base["QTESTGER"] == 0) & (base["OBSFL"] == "FL")
        ]
        corteLivre = DfCompleto.loc[(DfCompleto["CATEGORIAS"] == "Livre") &  (base['SUPDT'] == 'sup')]
        CorteResto = base.loc[~(base["CODPROD"].isin(corteLivre["CODPROD"]))]

        codigos = list(corteLivre["CODPROD"].drop_duplicates())
        print(codigos)

        with pd.ExcelWriter(OutPut.Jupyter_1) as save:
            corteLivre.to_excel(save, sheet_name="RETIRADA", index=False)
            CorteResto.to_excel(save, sheet_name="ValidarProd", index=False)
            self.ValvulaSave = True
        return codigos

    def automact(self, lista):
        Aux.limpar_terminal()
        dados = self.__pipeline(lista)
        input("Aperte [ENTER] para continuar...")

        Aux.limpar_terminal()

        trava = 0.2
        if dados:
            print(
                "\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n"
            )

            for segundos_restantes in range(5, 0, -1):
                print(
                    f"\rIniciando disparos em {segundos_restantes}s... NÃO MEXA NO MOUSE OU TECLADO!",
                    end="",
                    flush=True,
                )
                pag.sleep(1.0)
            print("\n\n[STATUS] Automação em andamento...")
            total = len(dados)
            for fase, registro in enumerate(dados, 1):
                Aux.verificarcopy(registro)
                pag.press("enter")
                pag.sleep(trava)

                pag.press("tab")
                pag.sleep(trava)

                pag.press("enter")
                pag.sleep(trava)

                for _ in range(7):
                    pag.press("tab")
                    pag.sleep(trava)

                pag.press("enter")
                pag.sleep(trava)

                pag.press("tab")
                pag.sleep(trava)

                for _ in range(2):
                    pag.press("enter")
                    pag.sleep(trava)

                pag.hotkey("shift", "tab")
                pag.sleep(trava)

                pag.press("enter")
                pag.sleep(trava)
                print(
                    f"\rProgresso: [{fase}/{total}] - Itens restantes: {total - fase} ",
                    end="",
                    flush=True,
                )
        else:
            print(
                "[AVISO] Nenhum registro válido encontrado para esta modalidade."
            )
            if self.ValvulaSave:
                resposta = input("\nArquivo gerado, deseja abrir o arquivo? (S/N): ").strip().upper()
                
                if resposta in ["S", "SIM", "s"]:
                    os.startfile(OutPut.Jupyter_1)
                    print("Arquivo aberto com sucesso!")
                else:
                    print("Fim!")
                    input()
class Capacidade:
    def __init__(self):
        Aux.limpar_terminal()
        self.col = ["CODPROD","PL_LASTRO","PL","CAP","QTEnd","V_CAP"]
        self.valvula = False
        self.executar()

    def automact(self, _listaProd_, _ListaFora_, _cap_):
        trava = 0.1
        total = len(_listaProd_)
        for fase, registro in enumerate(_listaProd_, 1):
            Aux.verificarcopy(registro["CODPROD"])
            pag.press("enter") 
            pag.sleep(trava)
            
            pag.press("tab")
            pag.sleep(trava)
            pag.press("enter") 

            Aux.verificarcopy(registro[_cap_])
            pag.press("enter")
            pag.sleep(trava)

            Aux.verificarcopy(registro["PONTO"])
            pag.press("enter")
            pag.sleep(trava)

            pag.press("enter")
            pag.sleep(trava)

            print(f"\rProgresso: [{fase}/{total}] - Itens restantes: {total - fase} ",end="",flush=True)

    def Pipeline(self):
        try:
            dados = pd.read_excel(OutPut.Cadastro,usecols=self.col,sheet_name="cadastro")
            enderecado = pd.read_csv(Wms.endereco07, header=None, names=ColNames.Endereco)

            end = enderecado[["DISP", "COD", "ENTRADA", "SAIDA"]].copy()
            for var in ["DISP", "ENTRADA", "SAIDA"]:
                end[var] = (
                    end[var]
                    .astype(str)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .astype(float)
                )

            end["PEDENTE"] = (end["ENTRADA"] + end["SAIDA"]).astype(float)
            vazio = (end["DISP"] == 0) & (end["PEDENTE"] == 0)
            ocupado = (end["DISP"] > 0) & (end["PEDENTE"] == 0)
            pedente = end["PEDENTE"] > 0
            categoria = [vazio, ocupado, pedente]
            var = ["VAZIO", "OCUPADO", "PEDENCIA"]
            end["CATEGORIA"] = np.select(categoria, var, default="Anomalia")

            dados = dados.merge(
                end, left_on="CODPROD", right_on="COD", how="left"
            )

            listnome = []
            listDt = []
            paths = [OutPut.Cadastro, Wms.endereco07]
            for caminho in paths:
                nome = os.path.basename(caminho)
                timestamp = os.path.getmtime(caminho)
                data_formatada = datetime.fromtimestamp(timestamp).strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
                listnome.append(nome)
                listDt.append(data_formatada)

            print("=" * 60)
            for etapa in range(len(paths)):
                print(f"[ARQUIVO]: {listnome[etapa]}")
                print(f"[MODIFICADO EM]: {listDt[etapa]}")
            print("=" * 60 + "\n")

            dfUP = dados.loc[(dados["V_CAP"] == "DIV_UP") & (dados["QTEnd"] == 2) & (dados["CATEGORIA"] != "PEDENCIA")].copy()
            dfUP["PONTO"] = round(dfUP["PL"] * 0.3, 0).astype(int)
            dfUP = dfUP.drop_duplicates(subset=["CODPROD"], keep="first")
            lista_UP = dfUP[["CODPROD", "PL", "PONTO", "CATEGORIA", "V_CAP"]].to_dict(orient="records")

            dfDOWN = dados.loc[(dados["V_CAP"] == "DIV_DOWN") & (dados["QTEnd"] == 2) & (dados["CATEGORIA"] != "PEDENCIA")].copy()
            dfDOWN["PONTO"] = round(dfDOWN["PL"] * 0.3, 0).astype(int)
            dfDOWN = dfDOWN.drop_duplicates(subset=["CODPROD"], keep="first")
            lista_DOWN = dfDOWN[["CODPROD", "PL_LASTRO", "PONTO", "CATEGORIA", "V_CAP"]].to_dict(orient="records")

            contagemUP = dfUP["CODPROD"].nunique()
            contagemDOWN = dfDOWN["CODPROD"].nunique()

            print(f">> Encontrados no DFUP: {contagemUP} item(s)")
            print(f">> Encontrados no DFDOWN: {contagemDOWN} item(s)")
            print(("=" * 19 ) + " SELEÇÃO DE MODALIDADE " + ("=" * 19))
            print(" 1 - 'DF_UP' (Usará PL) | 2 - 'DF_DOWN' (Usará PL_LASTRO)")
            print("-" * 61)
            while True:
                escolha = input("Digite a opção desejada (1 ou 2): ").strip()
                if escolha == "1":
                    capacidade = "PL"
                    listaMOD = lista_UP
                    break
                elif escolha == "2":
                    capacidade = "PL_LASTRO"
                    listaMOD = lista_DOWN
                    break
                else:
                    print("[ALERTA] Opção inválida! Digite estritamente 1 ou 2.")
            self.valvula = True
            return capacidade, listaMOD
        except Exception as e:
            print(f"\n[ERRO CRÍTICO] Houve um erro na etapa de dados: {e}")
            self.valvula = False
            listaMOD = []
    def executar(self):
        try:
            capacidade, listaMOD = self.Pipeline()
            if not self.valvula:
                print("sem ação")
                input("")
                return
            listaFora = {"Produto": None, "CATEGORIA": None}
            Aux.limpar_terminal()

            print("=" * 60)
            print(f">> TOTAL DE REGISTROS A PROCESSAR: {len(listaMOD)}")
            print("=" * 60 + "\n")

            if listaMOD:
                input(">> Prepare a tela do sistema e pressione [ENTER] para continuar...")
                print("\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n")

                for segundos_restantes in range(5, 0, -1):
                    print(f"\rIniciando disparos em {segundos_restantes}s... NÃO MEXA NO MOUSE OU TECLADO!",end="",flush=True,)
                    pag.sleep(1.0)

                print("\n\n[STATUS] Automação em andamento...")
                self.automact(_listaProd_= listaMOD, _ListaFora_= listaFora, _cap_= capacidade)
            else:
                print(
                    "[AVISO] Nenhum registro válido encontrado para esta modalidade."
                )

        except Exception as e:
            print(f"\n\n[ERRO] Falha durante a execução dos cliques: {e}")

        print("\n\n" + "=" * 60)
        print("[SUCESSO] O script finalizou as tentativas de processamento.")
        print("=" * 60)
        input("\nPressione [ENTER] para fechar esta janela com segurança...")

def main():
    while True:
        Aux.limpar_terminal()
        print("Automação Rotina 3706\n")
        print("Escolha uma das opções abaixo:")
        print("1 - Retirada de endereços.")
        print("2 - Ajuste de capacidade.")
        print("0 - Cancelar.\n")

        escolha = input(">> ").strip()

        if escolha == "1":
            RetirarEndereco()
        elif escolha == "2":
            Capacidade()
        elif escolha == "0":
            print("Fechando...")
            time.sleep(0.7)
            break
        else:
            print("Opção inválida! Digite 1, 2 ou 0.")
            time.sleep(1)


if __name__ == "__main__":
    main()