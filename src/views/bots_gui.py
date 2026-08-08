from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))

import tkinter as tk
from bot import ExeBots
# from ..lib import ValidarErros
# from src.lib.settings import Assets

"""
Criação da interface onde vai realizar a mesma logica dos modulos
procurar na pasta bot os modulos e depois criar bt para cada 
"""

class Aux:
    "Separar as ação da interface da construção dos componentes"
    pass

class GUI_autobot:
    def __init__(self):
        self.mapaKeys = ExeBots()
        self.listBTS = []

        self.background = "#2F4F4F"
        self.frame_color = "#F0FFFF"
        self.borda_color = "#000000"
        self.back_2 = "#363636"
        self.estilo_alerta = {"foreground": "#FF640A", "font": ("Consolas", 16, "bold"), "justify": "center"}

        root = tk.Tk()
        root.title("Central de Automação")
        root.geometry("500x400")
        root.resizable(False,False)
        root.config(bg= self.background)
        # root.iconbitmap(Assets.IcoPrincipal)
        # chaves = mapa.keys()


        self.Componentes(root)
        self.Clicaveis(root)
        self.Localizar()
        root.mainloop()
        pass

    def Componentes(self, Tela):
        self.TelaPrincipal = tk.Frame(
            Tela
            ,bg= self.frame_color
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )
        self.telaBTs = tk.Frame(
            self.TelaPrincipal
            ,bg= self.frame_color
        )
        self.telaOBS = tk.Label(
            self.TelaPrincipal
            ,bg= self.back_2
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )
        pass
    def Clicaveis(self, Tela):
        for item in self.mapaKeys.keys():
            btetapa = tk.Button(
            self.telaBTs
            ,text= self.mapaKeys[item]['Nome']
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: self.mapaKeys[item]['Classe']
            )
            self.listBTS.append(btetapa)
            
    def Localizar(self):
        self.TelaPrincipal.place(rely= 0.01, relx= 0.02, relheight= 0.98, relwidth= 0.96)

        self.telaOBS.place(rely= 0.50, relx= 0.01, relheight= 0.49, relwidth= 0.98)
        self.telaBTs.place(rely= 0.01, relx= 0.01, relheight= 0.48, relwidth= 0.98)

        """"""
        colunas = 3
        largura_btn = 0.30
        altura_btn = 0.30

        passo_x = 0.33  # 0.30 + 0.03 de folga horizontal
        passo_y = 0.33  # 0.30 + 0.03 de folga vertical

        for i, item in enumerate(self.listBTS):
            coluna = i % colunas
            linha = i // colunas

            rx = 0.01 + (coluna * passo_x)
            ry = 0.01 + (linha * passo_y)

            item.place(rely=ry, relx=rx, relheight=altura_btn, relwidth=largura_btn)

if __name__ == "__main__":
    GUI_autobot()