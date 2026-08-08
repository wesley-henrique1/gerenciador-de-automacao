from ..lib import ValidarErros

import pyautogui as pag
import pyperclip as pc
import threading
import time

import tkinter as tk 
from tkinter import messagebox


class Flow1702:
    validador = ValidarErros(fonte="Flow 1702")
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
    
    def _Finalizar(self, Bool, Sku, temp):
        try:
            total_bool = len(Bool)
            total_sku = len(Sku)
            fim_processo = time.time()
            tempo_total = fim_processo - temp

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
                    f"Último Código: {Bool[-1]}\n"
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
        except Exception as e:
           self.validador.registrar_log(e, "logic: _Finalizador") 

        pass
    def _automact(self, listaSKU, Maximo):
        try:
            Inicio_processo = time.time()

            lista_bool = []
            
            pag.keyDown('alt')
            pag.press('tab')
            pag.keyUp('alt')
            pag.sleep(0.5)

            for etapa, SKU in enumerate(listaSKU):
                if not self.em_execucao:
                    break
                progresso_anterior = int((etapa / Maximo) * 100)
                MSG = (
                    f"{f">> PROGRESSO: {etapa} - {Maximo} || {progresso_anterior}%":<}\n"
                    f"{f">> PRODUTO: {SKU}":<}"
                )
                self.ancoraContador.config(text= MSG)

                if not self.em_execucao: break
                pc.copy(SKU)
                pag.hotkey("ctrl", "v")
                pag.press('enter')
                time.sleep(self.time_executar)

                if not self.em_execucao: break
                pag.press('right')
                time.sleep(self.time_executar)

                if not self.em_execucao: break
                pag.press('enter')
                pag.press('enter')
                time.sleep(self.time_executar)

                if not self.em_execucao: break

                progresso_atual = int(( (etapa +1) / Maximo) * 100)
                MSG = (
                    f"{f">> PROGRESSO: {etapa +1} - {Maximo} || {progresso_atual}%":<}\n"
                    f"{f">> PRODUTO: {SKU}":<}"
                )
                self.ancoraContador.config(text= MSG)
                lista_bool.append(SKU)
            
            self._Finalizar(Bool= lista_bool, Sku= listaSKU, temp= Inicio_processo)
        except Exception as e:
           self.validador.registrar_log(e, "logic: _automact") 
        pass

    def PararProcesso(self):
        try:
            self.em_execucao = False

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
        pass
