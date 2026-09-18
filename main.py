from src.lib.settings import Assets
from src.views import Demandas, Ui1731, Ui3707, Ui1702, PainelLog
from src.mod import Executar
from src.lib import Processador, ValidarErros

from tkinter import scrolledtext, messagebox
import tkinter as tk


class auxiliar:       
    def _exibir_mensagem_status(self, mensagem):
        self.retorno.config(state="normal")
        self.retorno.delete("1.0", "end")
        self.retorno.insert("1.0", mensagem)
        self.retorno.tag_add("alerta", "1.0", "end")
        self.retorno.tag_config("alerta", **self.estilo_alerta)
        self.retorno.config(state="disabled")        
    def start_UI(self):
        selecionados = [nome for nome, var in self.estados.items() if var.get()]
        try:
            if not selecionados:
                messagebox.showwarning("Aviso", "Selecione ao menos uma opção!")
                return
            self.logica_UI.executar_threads(selecionados)
        except Exception as e:
            self.validador.registrar_log(e, "Main-start_UI")
    def resetar_UI(self):
        for var in self.estados:
            self.estados[var].set(False)
        
        self._exibir_mensagem_status("Aguardando proximo processo...")
        self.retorno_db.config(state="normal")
        self.retorno_db.delete("1.0", "end")
        self.retorno_db.config(state="disabled")

        self.retorno_file.config(state="normal")
        self.retorno_file.delete("1.0", "end")
        self.retorno_file.config(state="disabled")


        self.contador.config(text="PROGRESSO >> 100% || 0/0 OPERAÇÃO")    
    pass
class JanelaPrincipal(auxiliar):
    validador = ValidarErros(fonte="main")
    def __init__(self):
        self.background = "#2F4F4F"
        self.frame_color = "#F0FFFF"
        self.borda_color = "#000000"
        self.back_2 = "#363636"
        self.estilo_alerta = {"foreground": "#FF640A", "font": ("Consolas", 16, "bold"), "justify": "center"}

        root = tk.Tk()
        root.title("GERENCIADOR_8000")
        root.geometry("938x538")
        root.resizable(False,False)
        root.config(bg= self.background)
        root.iconbitmap(Assets.IcoPrincipal)
        
        self.scripts_map, self.mapa_relacao = Executar()
        chaves = self.scripts_map.keys()

        self.list_check = []
        self.estados = {}

        for var in chaves:
            self.estados[var] = tk.BooleanVar(value=False)        

        self.quadro_fleg(janela_principal= root)
        self.quadro_bt(janela_principal= root)
        self.quadro_retorno(janela_principal= root)
        self.localizador()

        self.logica_UI = Processador(self)
        root.mainloop()
        pass

    def quadro_fleg(self, janela_principal):
        font = ("verdana", 9,"bold")

        self.parte_1 = tk.Frame(
            janela_principal
            ,bg= self.frame_color
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )

        for chave_interna, texto_exibicao in self.mapa_relacao.items():
            var_estado = self.estados.get(chave_interna)
            check = tk.Checkbutton(
                self.parte_1,
                text=texto_exibicao,
                variable=var_estado,
                font=font,
                bg=self.frame_color,
                fg=self.borda_color,
                selectcolor=self.frame_color,
                activebackground=self.frame_color,
                activeforeground=self.borda_color,
                justify="left"
                ,anchor= 'w'
            )
            self.list_check.append(check)
        pass
    def quadro_bt(self, janela_principal):
        self.parte_2 = tk.Frame(
            janela_principal
            ,bg= self.frame_color
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )
        self.bt_iniciar = tk.Button(
            self.parte_2
            ,text="INICIAR"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: self.start_UI()
        )
        self.bt_demanda = tk.Button(
            self.parte_2
            ,text= "CHECKLIST"
            ,cursor= "hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: Demandas()
        )
        self.bt_info = tk.Button(
            self.parte_2
            ,text= "ROTINAS"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: self.tela_ROTINAS()

        )
        self.bt_limpar = tk.Button(
            self.parte_2
            ,text="LIMPAR"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: self.resetar_UI()
        )
        
        self.automact = tk.Label(
            self.parte_2
            ,text= "AUTOMAÇÃO"
            ,font= ("verdana", 10, "bold")
            ,anchor= "n"
            ,bg= self.back_2
            ,fg= self.frame_color
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )
        self.bt_inv = tk.Button(
            self.automact
            ,text="1731"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: Ui1731()
        )
        self.bt_07 = tk.Button(
            self.automact
            ,text="3707"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: Ui3707()
        )
        self.bt1702 = tk.Button(
            self.automact
            ,text="1702"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: Ui1702()
        )

        pass
    def quadro_retorno(self, janela_principal):
        self.parte_3 = tk.Frame(
            janela_principal
            ,bg= self.frame_color
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )
        self.contador = tk.Label(
            self.parte_3
            ,text= "PROGRESSO >> 100% || 0/0 OPERAÇÃO"
            ,font= ("Consolas", 12)
            ,fg= self.frame_color
            ,bg= self.background
            ,anchor = "w"
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )
        self.retorno = tk.Text(
            self.parte_3
            ,font=("Consolas", 10)
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,highlightthickness=2
            ,padx=10, pady=10
            ,state="disabled"
        )
        self.retorno_db = tk.Text(
            self.parte_3
            ,font=("Consolas", 10)
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,highlightthickness=2
            ,padx=10, pady=10
            ,state="disabled"
        )
        self.retorno_file = tk.Text(
            self.parte_3
            ,font=("Consolas", 10)
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,highlightthickness=2
            ,padx=10, pady=10
            ,state="disabled"
        )
        pass
    
    def tela_ROTINAS(self):
        # Cria a janela pop-up
        janela_info = tk.Toplevel()
        janela_info.title("ROTINAS")
        janela_info.geometry("400x300")
        janela_info.resizable(False,False)
        janela_info.configure(bg=self.background)
        janela_info.iconbitmap(Assets.IcoEngrenagem)

        self.frame_rotina = tk.Frame(
            janela_info
            ,bg= self.frame_color
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )
        self.conteudo_rotina = scrolledtext.ScrolledText(
             self.frame_rotina
            ,width=110, height=35
            ,font=("Consolas", 14)
        )
        conteudo_formatado = (
            f"{"_" * 34}\n"
            f"|{"Abastecimento: 8628, 8664.":<}\n"
            f"|{"Corte: 1767, 8041.":<}\n"
            f"|{"Cadastro: 8596.":<}\n"
            f"|{"Giro estoque: 8596, 286, 1707.":<}\n"
            f"|{"Acuracidade: 286, 8596, 1707.":<}\n"
            f"|{"Ordem de serviço: 8628, 1707.":<}\n"
            f"|{"Cheio x Vazio: sem rotinas.":<}\n"
            f"|{"Inventario: 1733.":<}\n"
            f"{"_" * 34}\n"
        )
        self.conteudo_rotina.insert(tk.INSERT, conteudo_formatado)
        self.conteudo_rotina.configure(state='disabled')

        self.frame_rotina.place(relx= 0.02, rely= 0.01, relheight= 0.96, relwidth= 0.96)
        self.conteudo_rotina.place(relx= 0.01, rely= 0.01, relheight= 0.98, relwidth= 0.98)
        pass
    def tela_CORTE(self, titulo, conteudo_formatado):
        # Cria a janela pop-up
        janela_info = tk.Toplevel()
        janela_info.title(titulo)
        janela_info.geometry("1020x500")
        janela_info.resizable(False,True)
        janela_info.configure(bg=self.back_2)
        janela_info.iconbitmap(Assets.IcoCorte)
        janela_info.attributes("-topmost", True)

        self.conteudo_corte = scrolledtext.ScrolledText(
            janela_info, 
            width=110, height=35, 
            font=("Consolas", 10),
            bg= self.back_2, 
            fg= self.frame_color
        )
        self.conteudo_corte.insert(tk.INSERT, conteudo_formatado)
        self.conteudo_corte.configure(state='disabled')

        self.conteudo_corte.place(relx= 0.01, rely= 0.01, relheight= 0.98, relwidth= 0.98)
        pass
    def ancoragemPanel(self, var):
        PainelLog(var)
    def localizador(self):
        # QUADRO 1 FLEXBOX
        self.parte_1.place(relx= 0.005, rely= 0.01, relwidth= 0.51, relheight= 0.30)

        _relx_T1 = 0.01
        _relx_T2 = 0.53

        _rely_inicial = 0.03
        _altura_item = 0.15
        total = round(len(self.list_check) / 2)
        for indice, item_check in enumerate(self.list_check):
            if indice < total:
                _relx = _relx_T1
                posicao_y = _rely_inicial + (indice * _altura_item)

            else:
                _relx = _relx_T2
                posicao_y = _rely_inicial + ((indice-total) * _altura_item)

            item_check.place(
                relx=_relx
                ,rely=posicao_y
                ,relheight=_altura_item
            )    

        # QUADRO 2 BOTÃO
        self.parte_2.place(relx= 0.520, rely= 0.01, relwidth= 0.475, relheight= 0.30)

        self.bt_iniciar.place(relx=0.02, rely=0.10, relwidth=0.22, relheight=0.20)
        self.bt_demanda.place(relx=0.266, rely=0.10, relwidth=0.22, relheight=0.20)
        self.bt_info.place(relx=0.512, rely=0.10, relwidth=0.22, relheight=0.20)
        self.bt_limpar.place(relx=0.758, rely=0.10, relwidth=0.22, relheight=0.20)

        self.automact.place(relx=0.01, rely=0.34, relwidth=0.98, relheight=0.65)
        self.bt_inv.place(relx=0.01, rely=0.20, relwidth=0.30, relheight=0.30)
        self.bt_07.place(relx=0.35, rely=0.20, relwidth=0.30, relheight=0.30)
        self.bt1702.place(relx=0.68, rely=0.20, relwidth=0.30, relheight=0.30)

        # QUADRO 3 RETORNOS
        self.parte_3.place(relx= 0.005, rely= 0.32, relwidth= 0.99, relheight= 0.67)

        self.contador.place(relx=0.005, rely=0.01, relwidth=0.99, relheight=0.10)

        self.retorno.place(relx=0.005, rely=0.15, relwidth=0.59, relheight=0.84)
        self.retorno_db.place(relx=0.60, rely=0.15, relwidth=0.394, relheight=0.38)
        self.retorno_file.place(relx=0.60, rely=0.55, relwidth=0.394, relheight=0.44)
        pass
    pass

if __name__ == "__main__":
    JanelaPrincipal()
