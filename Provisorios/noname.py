import time
import tkinter as tk
from tkinter import messagebox
import pyautogui


def processar():
    # Coleta os valores digitados nos campos
    cod = entry_cod.get().strip()
    alt = entry_alt.get().strip()
    larg = entry_larg.get().strip()
    comp = entry_comp.get().strip()
    alt_m = entry_alt_m.get().strip()
    larg_m = entry_larg_m.get().strip()
    comp_m = entry_comp_m.get().strip()

    campos = [cod, alt, larg, comp, alt_m, larg_m, comp_m]

    # Validação: verifica se todos os campos contêm apenas números (inteiros ou decimais)
    for valor in campos:
        if not valor:
            messagebox.showerror(
                "Erro de Validação", "Todos os campos devem ser preenchidos!"
            )
            return
        try:
            float(valor)
        except ValueError:
            messagebox.showerror(
                "Erro de Validação",
                f"O valor '{valor}' não é um número válido!",
            )
            return

    # Atribuição das variáveis numéricas
    COD = cod
    alt_val = alt
    larg_val = larg
    comp_val = comp
    altM = alt_m
    largM = larg_m
    compM = comp_m

    # Intervalo de 0.2 segundos entre cada ação do PyAutoGUI
    pyautogui.PAUSE = 0.2

    # Alt+Tab para mudar para a janela em segundo plano
    pyautogui.hotkey("alt", "tab")
    time.sleep(0.5)  # Pequeno tempo de espera para a janela alternar

    # Sequência de ações do teclado
    pyautogui.write(COD)
    pyautogui.press("enter")
    pyautogui.press("enter")
    pyautogui.press("tab")
    pyautogui.press("enter")

    pyautogui.write(alt_val)
    pyautogui.press("enter")

    pyautogui.write(larg_val)
    pyautogui.press("enter")

    pyautogui.write(comp_val)
    pyautogui.press("enter", presses=3)

    pyautogui.write(altM)
    pyautogui.press("enter")

    pyautogui.write(largM)
    pyautogui.press("enter")

    pyautogui.write(compM)
    pyautogui.press("enter", presses=3)

    pyautogui.press("tab", presses=3)
    pyautogui.press("enter", presses=2)

    # Alt+Tab para retornar à janela anterior
    pyautogui.hotkey("alt", "tab")


# Configuração da Janela Principal
root = tk.Tk()
root.title("AUTOMAÇÃO 3707")
root.geometry("400x350")
root.config(padx=15, pady=15)

# --- Linha 1: Cod_pro ---
frame_linha1 = tk.Frame(root)
frame_linha1.pack(fill="x", pady=5)

lbl_cod = tk.Label(frame_linha1, text="Cod_pro:")
lbl_cod.pack(side="left", padx=(0, 5))

entry_cod = tk.Entry(frame_linha1)
entry_cod.pack(side="left", fill="x", expand=True)

# --- Linha 2: Unidade ---
frame_unidade = tk.LabelFrame(root, text="Unidade", padx=10, pady=10)
frame_unidade.pack(fill="x", pady=5)

tk.Label(frame_unidade, text="Alt:").grid(row=0, column=0, sticky="w")
entry_alt = tk.Entry(frame_unidade, width=8)
entry_alt.grid(row=0, column=1, padx=(0, 10))

tk.Label(frame_unidade, text="Larg:").grid(row=0, column=2, sticky="w")
entry_larg = tk.Entry(frame_unidade, width=8)
entry_larg.grid(row=0, column=3, padx=(0, 10))

tk.Label(frame_unidade, text="Comp:").grid(row=0, column=4, sticky="w")
entry_comp = tk.Entry(frame_unidade, width=8)
entry_comp.grid(row=0, column=5)

# --- Linha 3: CX_Master ---
frame_cx_master = tk.LabelFrame(root, text="CX_Master", padx=10, pady=10)
frame_cx_master.pack(fill="x", pady=5)

tk.Label(frame_cx_master, text="Alt_M:").grid(row=0, column=0, sticky="w")
entry_alt_m = tk.Entry(frame_cx_master, width=8)
entry_alt_m.grid(row=0, column=1, padx=(0, 10))

tk.Label(frame_cx_master, text="Larg_M:").grid(row=0, column=2, sticky="w")
entry_larg_m = tk.Entry(frame_cx_master, width=8)
entry_larg_m.grid(row=0, column=3, padx=(0, 10))

tk.Label(frame_cx_master, text="Comp_M:").grid(row=0, column=4, sticky="w")
entry_comp_m = tk.Entry(frame_cx_master, width=8)
entry_comp_m.grid(row=0, column=5)

# --- Botão Processar ---
btn_processar = tk.Button(
    root, text="Processar", command=processar, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")
)
btn_processar.pack(pady=15, fill="x")

root.mainloop()