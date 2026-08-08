import pyautogui as pag
import pyperclip as pc
import threading
import time
from ..lib import ValidarErros
from tkinter import messagebox
import tkinter as tk

class Flow1731:
    validador = ValidarErros(fonte="Flow 1731")
    def __init__(self, UI):        
        self.UImodulo = UI
        self.TextLog = (
            f"{">> PROGRESSO: 0 - 0 || 100%":<}\n"
            f"{">> PRODUTO: ______":<}"
        )
        self.time_executar = 0.001

        self.ancoraIniciar = self.UImodulo.bt_iniciar
        self.ancoraContador = self.UImodulo.contador
        self.ancoraEntrada = self.UImodulo.entry_cod
        
        pass
    
    def PararProcesso(self):
        self.em_execucao = False
        try:
            self.ancoraIniciar.config(state="normal")
            self.ancoraEntrada.delete("1.0", tk.END)
            self.ancoraContador.config(text= self.TextLog)
        except Exception as e:
           self.validador.registrar_log(e, "logic: PararProcesso") 

        pass
    def IniciarProcesso(self, _listas):
        try:
            self.em_execucao = True
            self.ancoraIniciar.config(state="disabled")
            _codProd = []

            _lista = _listas.get("1.0", tk.END).strip().splitlines()
            contagem = len(_lista)

            if not _lista:
                messagebox.showerror("Aviso", "Lista esta vazia, favor informar os codigos")
                self.PararProcesso()
                return
            for var in _lista:
                try:
                    var = int(str(var).strip())
                    _codProd.append(var)
                except (ValueError, TypeError):
                    mensagem = f"Erro de Formato: O valor '{var}' não é um código válido.\n\nUse apenas números inteiros."
                    messagebox.showwarning("Divergência de Dados", mensagem)   
                    self.PararProcesso()
                    return

            self.em_execucao = True
            self.ancoraEntrada.delete("1.0", tk.END)
            threading.Thread(target= self._automact, args= (_codProd,contagem,), daemon= True).start()
        except Exception as e:
           self.validador.registrar_log(e, "logic: IniciarProcesso") 

    def _automact(self,lista_sku, maximo):
        inicio_processo = time.time()

        lista_bool = []
        pag.keyDown('alt')
        pag.press('tab')
        pag.keyUp('alt')
        pag.sleep(0.5)
        
        for etapa, SKU in enumerate(lista_sku):            
            if not self.em_execucao:
                break
            progresso_anterior = int((etapa / maximo) * 100)
            MSG = (
                f"{f">> PROGRESSO: {etapa} - {maximo} || {progresso_anterior}%":<}\n"
                f"{f">> PRODUTO: {SKU}":<}"
            )
            self.ancoraContador.config(text= MSG)

            pc.copy(SKU)
            pag.hotkey("ctrl", "v")
            pag.press('enter')
            time.sleep(self.time_executar)

            for _ in range(4):
                if not self.em_execucao: break
                pag.press('tab')
                time.sleep(self.time_executar)
            
            if not self.em_execucao: break
            pag.press('enter')

            for _ in range(3):
                if not self.em_execucao: break
                pag.press('tab')
                time.sleep(self.time_executar)

            if not self.em_execucao: break
            pag.press('enter')
            pag.press('tab')

            progresso_atual = int(( (etapa +1) / maximo) * 100)
            MSG = (
                f"{f">> PROGRESSO: {etapa +1} - {maximo} || {progresso_atual}%":<}\n"
                f"{f">> PRODUTO: {SKU}":<}"
            )
            self.ancoraContador.config(text= MSG)

            lista_bool.append(SKU)
        
        total_bool = len(lista_bool)
        total_sku = len(lista_sku)
        fim_processo = time.time()
        tempo_total = fim_processo - inicio_processo

        if tempo_total > 60:
            minutos, segundos = divmod(tempo_total, 60)
            msg = f"{int(minutos)}min e {int(segundos)} segundos"
        else:
            msg = f"{tempo_total:.2f} segundos"    

        if total_bool == total_sku:
                messagebox.showinfo(
                    "Sucesso", 
                    f"Processado: {total_bool} de {total_sku} itens.\n"
                    f"{'—'*25}\n"
                    f"Tempo de execução {msg}."
                )
                self.ancoraIniciar.config(state="normal")
        elif total_bool < total_sku:
            mensagem = (
                f"Resumo da Operação\n"
                f"{'—'*25}\n"
                f"Transferência: {total_bool} de {total_sku} SKUs\n"
                f"Último Código: {lista_bool[-1]}\n"
                f"Tempo de execução {msg}."
            )
            messagebox.showinfo("Finalizado parcialmente", mensagem)
            self.ancoraIniciar.config(state="normal")
        else:
            messagebox.showerror(
                "Erro na Transferência", 
                f"Apenas {total_bool} de {total_sku} itens foram processados.\n"
                "Verifique os logs para mais detalhes."
            )
            self.ancoraIniciar.config(state="normal")


