from pathlib import Path
import pandas as pd 

from src.lib import ValidarErros
import pyautogui as pag
import pyperclip as pc
import os

import pandas as pd
class auxiliar:
    def limpar_terminal() -> None:
        os.system("cls" if os.name == "nt" else "clear")

        pass
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
class FinalizarOS:
    validador = ValidarErros(fonte="ContagemINV")
    def __init__(self):
        self.velocidade = 0.3
        self.largura = 70

        caminho = Path(r"z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.6 - PCL Cadastro\Wesley Henrique\O_S PENDENTES.xlsx")
        self.listadados = [caminho]
        self.outra = []
        self.ExecutarBot(self.listadados, self.outra)

    def __Simulador(self, df: pd.DataFrame):
        try:
            lista = []
            total_itens = len(df)

            for fase, (ws, registro) in enumerate(df.iterrows(), 1):
                ordemServ = registro['NUMOS']

                if not auxiliar._copiar_e_validar(ordemServ):
                    print(f"\nErro ao copiar produto: {ordemServ}")
                    continue
                pag.sleep( self.velocidade)
                pag.hotkey("ctrl", "v")
                pag.sleep( self.velocidade)
                pag.press('enter')
                pag.sleep( self.velocidade)

                pag.press('tab')
                pag.sleep( self.velocidade)

                for tab in range(2):
                    pag.press('enter')

                matricula = registro['MATRICULA']
                if not auxiliar._copiar_e_validar(matricula):
                    print(f"\nErro ao copiar produto: {matricula}")
                    continue
                pag.sleep( self.velocidade)
                pag.hotkey("ctrl", "v")
                pag.sleep( self.velocidade)

                for tab in range(5):
                    pag.sleep( self.velocidade)
                    pag.press('enter')

                print(f"\rProgresso: [{fase}/{total_itens}] - Itens restantes: {total_itens - fase} ", end="", flush=True)
                lista.append(fase)

        except Exception as e:
            ValidarErros(e, etapa="simulador")
    def __pipeline(self, listaPath: list[str], listaSave: list[str]):
        try:
            dados = pd.read_excel(listaPath[0], sheet_name= 'EXTRATO', usecols= ['NUMOS', 'Tipo O.S.'])
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            dados = dados.drop_duplicates(subset= 'NUMOS', keep= "first")
            dados = dados.dropna(subset= 'NUMOS')
            dados =dados.sort_values(by= 'NUMOS', ascending= True)
            dados['MATRICULA'] = 180109
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            temp = listaSave
            return dados
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False

    def ExecutarBot(self, listaPath: list[str], listaSave: list[str]):
        auxiliar.limpar_terminal()
        produtos = self.__pipeline(listaPath=listaPath, listaSave= listaSave)

        if produtos.empty:
            print("Não foram encontrados produtos para transferência.")
            return
        qtde = produtos['NUMOS'].nunique()
        print(f"Quantidade de o.s a serem Finalizado: {qtde}")
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
        pass
