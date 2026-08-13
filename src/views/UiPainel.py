from ..lib import ValidarErros
from src.lib.settings import Assets
import tkinter as tk
from tkinter import messagebox
import time
import subprocess
import os 

class PainelLog:
    validador = ValidarErros(fonte="Painel Operação")

    def __init__(self, mapa):
        self.background = "#2F4F4F"
        self.frame_color = "#F0FFFF"
        self.borda_color = "#000000"
        self.back_2 = "#363636"
        self.estilo_alerta = {"foreground": "#FF640A", "font": ("Consolas", 16, "bold"), "justify": "center"}

        self.list_check = []
        self.list_estados = []

        self.mapa_relacao = {}
        self.boolchecks = {}
        self.estados = {}
        self.path = {}

        root = tk.Toplevel()
        root.title("Resumo Operação")
        root.geometry("400x300")
        root.resizable(False,False)
        root.config(bg= self.background)
        root.iconbitmap(Assets.IcoPrincipal)
        chaves = mapa.keys()

        for var in chaves:
            self.mapa_relacao[var] = mapa[var]["nomeclatura"]
            self.boolchecks[var] = tk.BooleanVar(value=False)  
            self.estados[var] = mapa[var]['estado']
            self.path[var] = mapa[var]["path"]

        self.componentes(root)
        self.Clicaveis(root)
        self.executaveis()
        self.Localizar()
        
        pass
    def start_UI(self):
        selecionados = [nome for nome, var in self.boolchecks.items() if var.get()]
        """
            etapa: abrir os arquivos de saida em ordem sem atropelamento, usar o time para fazer essa pausa
        """
        try:
            if not selecionados:
                messagebox.showwarning("Aviso", "Selecione ao menos uma opção!")
                return

            for var in selecionados:
                caminho = self.path[var]
                processo = subprocess.Popen(str(caminho), shell= True)
                if processo.poll() is None:
                    print(f"\nSucesso: O programa foi aberto e está rodando (PID: {processo.pid})")
                else:
                    print("\nAviso: O programa tentou abrir, mas fechou logo em seguida.")
                time.sleep(1)
                os.startfile(caminho)
        except Exception as e:
            self.validador.registrar_log(e, "Painel-start_UI")

        pass
    def executaveis(self):
        for chave_interna, texto_exibicao in self.mapa_relacao.items():
            var_estado = self.boolchecks.get(chave_interna)
            check = tk.Checkbutton(
                self.back,
                text=texto_exibicao,
                variable=var_estado,
                font= ("verdana", 9,"bold"),
                bg=self.frame_color,
                fg=self.borda_color,
                selectcolor=self.frame_color,
                activebackground=self.frame_color,
                activeforeground=self.borda_color,
                justify="left"
                ,anchor= 'w'
            )
            self.list_check.append(check)

        for chave_interna, texto_exibicao in self.estados.items():
            bloco = tk.Label(
                self.log,
                text=f"{chave_interna}: {texto_exibicao}",
                font= ("verdana", 8),
                bg=self.frame_color,
                fg=self.borda_color,
                justify="left"
                ,anchor= 'w'
                ,padx= 0.5
                ,pady= 0.5
            )
            self.list_estados.append(bloco)


        _relx_T1 = 0.01
        _relx_T2 = 0.53

        _rely_inicial = 0.03
        _altura_item = 0.15
        _salto_linha = 0.25

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
            pass

        total = round(len(self.list_estados) / 2)
        for var, bloco in enumerate(self.list_estados):
            if var < total:
                _relx = _relx_T1
                posicao_y = _rely_inicial + (var * _salto_linha)
            else:
                _relx = _relx_T2
                posicao_y = _rely_inicial + ((var - total) * _salto_linha)

            bloco.place(
                relx=_relx,
                rely=posicao_y,
                relheight=_altura_item
            )   
            pass
        pass
    def componentes(self, janela_principal):
        self.back = tk.Frame(
            janela_principal
            ,bg= self.frame_color
            ,highlightbackground= self.borda_color
            ,highlightthickness= 3
        )
        self.log = tk.Frame(
            janela_principal
            ,bg=self.frame_color
            ,highlightbackground=self.borda_color
            ,highlightthickness=2
            ,padx=10, pady=10
        )
        

        pass
    def Clicaveis(self, janela_principal):
        self.bt_iniciar = tk.Button(
            janela_principal
            ,text="Abrir Arquivos Prontos"
            ,cursor="hand2"
            ,relief="solid"
            ,font=("Arial", 10, "bold")
            ,highlightthickness=3
            
            ,bg=self.frame_color
            ,fg=self.borda_color
            ,highlightbackground=self.borda_color
            ,command=lambda: self.start_UI()
        )

        pass
    def Localizar(self):
        self.back.place(relx= 0.01, rely= 0.01, relheight= 0.50, relwidth= 0.98)
        self.log.place(relx= 0.01, rely= 0.52, relheight= 0.30, relwidth= 0.98)
        self.bt_iniciar.place(relx= 0.01, rely= 0.84, relheight= 0.15, relwidth= 0.98)
        
