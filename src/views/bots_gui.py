import tkinter as tk
# from ..lib import ValidarErros
# from src.lib.settings import Assets


class Aux:
    "Separar as ação da interface da construção dos componentes"
    pass

class GUI_autobot:
    def __init__(self):
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
        
        pass
    def Localizar(self):
        self.TelaPrincipal.place(rely= 0.01, relx= 0.02, relheight= 0.98, relwidth= 0.96)

        self.telaOBS.place(rely= 0.50, relx= 0.01, relheight= 0.49, relwidth= 0.98)
        self.telaBTs.place(rely= 0.01, relx= 0.01, relheight= 0.48, relwidth= 0.98)
        pass

if __name__ == "__main__":
    GUI_autobot()