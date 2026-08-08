from ..lib.settings import Assets
from ..lib import ValidarErros
from ..bot import  flow3707
import tkinter as tk

class Ui3707:
    validador = ValidarErros(fonte="interface flow 3707")
    def __init__(self):
        self.fonte = ("verdana", 9,"bold") 
        self.background = "#2F4F4F"
        self.frame_color = "#F0FFFF"
        self.borda_color = "#000000"
        self.back_2 = "#363636"
        self.estilo_alerta = {"foreground": "#FF640A", "font": ("Consolas", 12, "bold")}

        self.text_logUI = (
            f"{">> PROGRESSO: 0 - 0 || 100%":<}\n"
            f"{">> Fase: PRODUTO | DESTINO"}"
        )
        self.time_executar = 0.05

        root = tk.Tk()
        root.title("Flow_Feeder")
        root.geometry("300x210")
        root.resizable(False, False)
        root.config(bg=self.back_2)
        root.iconbitmap(Assets.IcoEngrenagem)
        
        self.componentes(root)
        self.clicaveis()
        self.localizar()

        self.ancora = flow3707.Flow3707(self)
        root.mainloop()
        pass

    def componentes(self, tela):
        self.tela_Segundaria = tk.Frame(
            tela
            ,bg= self.background
            ,highlightbackground= self.frame_color
            ,highlightthickness= 3
        )

        self.text_PROD = tk.Label(
            self.tela_Segundaria
            ,text= "Lista Produto:"
            ,font=("verdana", 10, "bold")
            ,bg=self.background
            ,fg=self.frame_color
            ,anchor= "nw"
            ,justify="left"
            ,padx=5
            ,pady=5
        )
        self.text_END = tk.Label(
            self.tela_Segundaria
            ,text= "Lista Destino:"
            ,font=("verdana", 10, "bold")
            ,bg=self.background
            ,fg=self.frame_color
            ,anchor= "nw"
            ,justify="left"
            ,padx=5
            ,pady=5
        )
        self.CodProd = tk.Text(
            self.tela_Segundaria
            ,font=("Consolas", 10)
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,highlightthickness=2
            ,padx=10, pady=10
        )
        self.CodEnd = tk.Text(
            self.tela_Segundaria
            ,font=("Consolas", 10)
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,highlightthickness=2
            ,padx=10, pady=10
        )
        
        self.logUI = tk.Label(
            self.tela_Segundaria
            ,text= self.text_logUI
            ,font= ("verdana", 10, "bold")
            ,bg= self.back_2
            ,fg= self.frame_color
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
            ,anchor= "nw"
            ,justify="left"
            ,padx=5
            ,pady=5
        )
        
        pass
    def clicaveis(self):
        self.btTransferir = tk.Button(
            self.tela_Segundaria
            ,text= "Transferir"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: self.ancora.IniciarProcesso(listCod= self.CodProd, listEnd= self.CodEnd)
        )
        self.btParar = tk.Button(
            self.tela_Segundaria
            ,text= "Parar"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: self.ancora.PararProcesso()
        )
        pass
    def localizar(self):
        self.tela_Segundaria.place(relx= 0.02, rely= 0.01, relwidth= 0.96, relheight= 0.98)
        
        self.text_PROD.place(relx= 0.02, rely= 0.01, relwidth= 0.40, relheight= 0.20)
        self.text_END.place(relx= 0.02, rely= 0.24, relwidth= 0.40, relheight= 0.20)
        self.CodProd.place(relx= 0.42, rely= 0.01, relwidth= 0.55, relheight= 0.20)
        self.CodEnd.place(relx= 0.42, rely= 0.24, relwidth= 0.55, relheight= 0.20)

        self.logUI.place(relx= 0.02, rely= 0.46, relwidth= 0.95, relheight= 0.25)

        self.btTransferir.place(relx=0.19, rely=0.80, relwidth=0.30, relheight=0.15)
        self.btParar.place(relx=0.51, rely=0.80, relwidth=0.30, relheight=0.15)
