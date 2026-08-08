from ..lib import ValidarErros
import tkinter as tk
from tkinter import messagebox
import pyautogui as pag
import pyperclip as pc
import threading
import time
import pandas as pd
from datetime import timedelta

# Configurações globais de segurança do PyAutoGUI
pag.FAILSAFE = True      # Mover o mouse para o canto (0,0) aborta o script
pag.PAUSE = 0.2          # Pequena pausa automática entre comandos pyautogui

class Flow3707:
    validador = ValidarErros(fonte="logica Flow 3707")

    def __init__(self, UI):
        self.ancora = UI
        self.text_logUI = (
            f"{'>> PROGRESSO: 0 - 0 || 100%':<}\n"
            f"{'>> Fase: PRODUTO | DESTINO'}"
        )
        self.time_executar = 1

        self._codProd = []
        self._codEnd = []
        self.em_execucao = False

        self.AncoraCodProd = self.ancora.CodProd
        self.AncoraCodEnd = self.ancora.CodEnd
        self.AncoraLogUI = self.ancora.logUI
        self.AncoraBtTransferir = self.ancora.btTransferir

    def _SafeLogUI(self, fase, barramento, progresso, cod, end):
        """Atualização segura da interface GUI usando um widget Tkinter para o .after()"""
        MSG = (
            f"{f'>> PROGRESSO: {fase} - {barramento} || {progresso}%':<}\n"
            f"{f'>> PRODUTO: {cod} | {end}':<}"
        )
        # Usamos AncoraLogUI.after em vez de ancora.after
        self.AncoraLogUI.after(0, lambda: self.AncoraLogUI.config(text=MSG))

    def _SafeConfigUI(self, widget, **kwargs):
        """Método auxiliar para modificar a UI de forma thread-safe."""
        widget.after(0, lambda: widget.config(**kwargs))

    def _infoFinal(self, listaBool, end, processo):
        total_bool = len(listaBool)
        total_sku = len(end)

        fim_processo = time.time()
        tempo_total = fim_processo - processo
        msg = str(timedelta(seconds=int(tempo_total)))

        def exibir_mensagem():
            if total_bool == total_sku:
                messagebox.showinfo(
                    "Sucesso", 
                    f"Processado: {total_bool} de {total_sku} itens.\n"
                    f"{'—'*25}\n"
                    f"Tempo de execução: {msg}."
                )
            elif total_bool < total_sku:
                ultimo = listaBool[-1] if listaBool else "Nenhum"
                mensagem = (
                    f"Resumo da Operação\n"
                    f"{'—'*25}\n"
                    f"Transferência: {total_bool} de {total_sku} SKUs\n"
                    f"Último Código: {ultimo}\n"
                    f"Tempo de execução: {msg}."
                )
                messagebox.showinfo("Finalizado parcialmente", mensagem)
            else:
                messagebox.showerror(
                    "Erro na Transferência", 
                    f"Apenas {total_bool} de {total_sku} itens foram processados.\n"
                    "Verifique os logs para mais detalhes."
                )
            self.AncoraBtTransferir.config(state="normal")

        # Chama a caixa de diálogo na Thread principal através do Tkinter Widget
        self.AncoraBtTransferir.after(0, exibir_mensagem)

    def _copiar_e_validar(self, valor, tentativas=5):
        """Garante que o valor foi devidamente copiado para a área de transferência."""
        str_valor = str(valor)
        pc.copy(str_valor)
        for _ in range(tentativas):
            if pc.paste() == str_valor:
                return True
            time.sleep(0.1)
            pc.copy(str_valor)
        return False

    def _tratar(self, list_prod, list_end):
        self._codProd.clear()
        self._codEnd.clear()

        if not list_prod or not list_end:
            messagebox.showerror("Erro", "Uma ou ambas as listas estão vazias!")
            self.PararProcesso() 
            return None

        for var in list_prod:
            try:
                self._codProd.append(str(var).strip())
            except Exception as e:
                self.validador.registrar_log(e, "Logica _tratar (PROD): ")
                self.PararProcesso() 
                return None

        for var in list_end:
            try:
                self._codEnd.append(str(var).strip())
            except Exception as e:
                self.validador.registrar_log(e, "Logica _tratar (END): ")
                self.PararProcesso() 
                return None

        TT_PROD = len(self._codProd)
        TT_end = len(self._codEnd)

        if TT_PROD != TT_end:
            mensagem = f"As listas possuem quantidades diferentes!\n\nProdutos: {TT_PROD}\nEndereços: {TT_end}"
            messagebox.showwarning("Divergência", mensagem)
            self.PararProcesso()
            return None

        return TT_PROD

    def _automact(self, listCod, listEnd, trava):
        inicio_processo = time.time()
        try:
            lista_bool = []

            # Contagem regressiva com verificação de cancelamento
            for segundos_restantes in range(5, 0, -1):
                if not self.em_execucao: 
                    return
                msg = (
                    f"{'Processo iniciado. Clique no campo':<28}\n"
                    f"{f'Iniciando em {segundos_restantes}s':<28}"
                )
                self._SafeConfigUI(self.AncoraLogUI, text=msg)
                time.sleep(1.0)

            for etapa, (codprod, codend) in enumerate(zip(listCod, listEnd)):
                if not self.em_execucao: 
                    break

                progresso_anterior = int((etapa / trava) * 100)
                self._SafeLogUI(
                    fase=etapa,
                    barramento=trava,
                    progresso=progresso_anterior,
                    cod=codprod,
                    end=codend
                )

                # --- ETAPA 1: Inserir Produto ---
                if not self._copiar_e_validar(codprod):
                    print(f"Erro ao copiar produto: {codprod}")

                # pag.press('enter')
                print(codprod)
                time.sleep(0.3)
                pag.hotkey("ctrl", "v")
                time.sleep(0.5)
                pag.press('enter')

                if not self.em_execucao: 
                    break

                # --- ETAPA 2: Inserir Endereço ---
                if not self._copiar_e_validar(codend):
                    print(f"Erro ao copiar endereço: {codend}")

                print(codend)
                time.sleep(0.3)

                pag.hotkey("ctrl", "v")
                time.sleep(0.5)

                # Envios sequenciais confirmando a etapa
                for _ in range(3):
                    if not self.em_execucao: 
                        break
                    time.sleep(0.5)  
                    pag.press('enter')

                if not self.em_execucao: 
                    break

                # Sucesso do item atual
                progresso_atual = int(((etapa + 1) / trava) * 100)
                self._SafeLogUI(
                    fase=etapa + 1,
                    barramento=trava,
                    progresso=progresso_atual,
                    cod=codprod,
                    end=codend
                )
                lista_bool.append(codprod)

            if self.em_execucao:
                self._infoFinal(lista_bool, listCod, inicio_processo)

        except pag.FailSafeException:
            print("Automação cancelada pelo usuário via FailSafe.")
            self.PararProcesso()
        except Exception as e:
            self.PararProcesso()
            self.validador.registrar_log(e, "Logica: _automact") 

    def PararProcesso(self):
        try:
            self.em_execucao = False  
            self._codProd.clear()
            self._codEnd.clear()            

            def atualizar_ui_parada():
                self.AncoraCodProd.delete("1.0", tk.END)
                self.AncoraCodEnd.delete("1.0", tk.END)
                self.AncoraBtTransferir.config(state="normal")
                self.AncoraLogUI.config(text=self.text_logUI)

            # Alterado de self.ancora.after para self.AncoraLogUI.after
            self.AncoraLogUI.after(0, atualizar_ui_parada)
        except Exception as e:
            self.validador.registrar_log(e, "Logica: PararProcesso")

        return self.em_execucao    

    def IniciarProcesso(self, listCod, listEnd):
        try:
            self.em_execucao = True
            
            # Obtém o conteúdo digitado
            list_prod = listCod.get("1.0", tk.END).strip().splitlines()
            list_end = listEnd.get("1.0", tk.END).strip().splitlines()

            # Valida entradas
            TT_PROD = self._tratar(list_prod=list_prod, list_end=list_end)
            if TT_PROD is None or TT_PROD == 0:
                return

            # Limpa campos na interface e bloqueia o botão
            self.AncoraBtTransferir.config(state="disabled")
            self.AncoraCodProd.delete("1.0", tk.END)
            self.AncoraCodEnd.delete("1.0", tk.END)
            self.AncoraLogUI.config(text=self.text_logUI)

            # Inicia thread em modo Daemon para não travar a saída do programa
            t = threading.Thread(
                target=self._automact, 
                args=(list(self._codProd), list(self._codEnd), TT_PROD),
                daemon=True
            )
            t.start()
        except Exception as e:
            self.validador.registrar_log(e, "Logica: IniciarProcesso")