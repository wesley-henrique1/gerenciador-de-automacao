from ..lib.settings import Assets
from ..bot import flow1731
import tkinter as tk

class Ui1731:
    def __init__(self):
        self.fonte = ("verdana", 9,"bold") 
        self.background = "#2F4F4F"
        self.frame_color = "#F0FFFF"
        self.borda_color = "#000000"
        self.back_2 = "#363636"
        self.estilo_alerta = {"foreground": "#FF640A", "font": ("Consolas", 12, "bold")}
        
        self.TextLog = (
            f"{">> PROGRESSO: 0 - 0 || 100%":<}\n"
            f"{">> PRODUTO: ______":<}"
        )

        root = tk.Tk()
        root.title("Flow_Master")
        root.geometry("300x210")
        root.resizable(False, False)
        root.config(bg=self.back_2)
        root.iconbitmap(Assets.IcoEngrenagem)


        self.componentes(root)
        self.widgets_clicaveis()
        self.localizador()

        self.ancora = flow1731.Flow1731(self)
        root.mainloop() 
    
        pass

    def componentes(self, janela):
        self.frame_fundo = tk.Frame(
            janela
            ,bg= self.background
            ,highlightbackground= self.frame_color
            ,highlightthickness= 3
        )
        self.entry_cod = tk.Text(
            self.frame_fundo
            ,font=("Consolas", 10)
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,highlightthickness=2
            ,padx=10, pady=10
        )
        self.contador = tk.Label(
            self.frame_fundo
            ,text= self.TextLog
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
    def widgets_clicaveis(self): 
        self.bt_iniciar = tk.Button(
            self.frame_fundo
            ,text="INICIAR"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda:self.ancora.IniciarProcesso(self.entry_cod)
        )
        self.bt_parar = tk.Button(
            self.frame_fundo
            ,text="PARAR"
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
    def localizador(self):
        self.frame_fundo.place(relx= 0.02, rely= 0.01, relwidth= 0.96, relheight= 0.98)

        self.entry_cod.place(relx= 0.01, rely= 0.01, relwidth= 0.98, relheight= 0.20)
        self.contador.place(relx= 0.01, rely= 0.32, relwidth= 0.98, relheight= 0.40)

        self.bt_iniciar.place(relx= 0.01, rely= 0.78, relwidth= 0.48, relheight= 0.20)
        self.bt_parar.place(relx= 0.51, rely= 0.78, relwidth= 0.48, relheight= 0.20)

        pass

if "__name__" == "__main__":
    Ui1731()