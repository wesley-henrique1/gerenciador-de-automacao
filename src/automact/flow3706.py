from src.lib.settings import OutPut, Wms, ColNames
from datetime import datetime
import pyautogui as pag
import pyperclip as pc
import pandas as pd
import numpy as np
import os

def Verificarcopy(valor):
    tentativas_prod = 0
    pc.copy(str(valor))
    pag.sleep(0.02)
    while pc.paste() != str(valor) and tentativas_prod < 5:
        pag.sleep(0.1)
        pc.copy(str(valor))
        tentativas_prod += 1

    pag.hotkey("ctrl", "v")
def limpar_terminal():
    os.system("cls" if os.name == "nt" else "clear")

# Começa limpando a sujeira inicial do terminal
limpar_terminal()

# --- ETAPA 1: TRATAMENTO DE DADOS ---
try:
    try:
        dados = pd.read_excel(OutPut.Cadastro, usecols=['CODPROD', 'PL_LASTRO', 'PL', 'CAP', 'FREQ_PROD', 'V_CAP'], sheet_name= 'cadastro')
        enderecado = pd.read_csv(Wms.endereco07, header= None, names= ColNames.Endereco)
    except Exception as e:
        print(f"Erro na extração: {e}")
    
    end = enderecado[['DISP','COD','ENTRADA','SAIDA']]
    for var in ['DISP', 'ENTRADA', 'SAIDA']:
        end[var] = end[var].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

    print(end.head())
    end['PEDENTE'] = (end['ENTRADA'] + end['SAIDA']).astype(float)
    vazio = (end['DISP'] == 0) & (end['PEDENTE'] == 0)
    ocupado = (end['DISP'] > 0) & (end['PEDENTE'] == 0)
    pedente = (end['PEDENTE'] > 0)
    categoria = [vazio, ocupado, pedente]
    var = ['VAZIO', 'OCUPADO', 'PEDENCIA']
    end['CATEGORIA'] = np.select(categoria, var, default= 'Anomalia')

    dados = dados.merge(end, left_on= 'CODPROD', right_on= 'COD', how= 'left')

    listnome = []
    listDt = []
    paths = [OutPut.Cadastro, Wms.endereco07]
    for caminho in paths:
            nome = os.path.basename(caminho)
            timestamp = os.path.getmtime(caminho)
            data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')
            listnome.append(nome)
            listDt.append(data_formatada)    
    # limpar_terminal()

    print("="*60)
    for etapa in range(len(paths)):
            print(f"[ARQUIVO]: {listnome[etapa]}")
            print(f"[MODIFICADO EM]: {listDt[etapa]}")
    print("="*60 + "\n")
    dfUP = dados.loc[(dados['V_CAP'] == 'DIV_UP') & (dados['FREQ_PROD'] == 2) & (dados['CATEGORIA'] != 'PEDENCIA')].copy()
    dfUP['PONTO'] = round(dfUP['PL'] * 0.3, 0).astype(int)
    dfUP = dfUP.drop_duplicates(subset=['CODPROD'], keep='first')
    lista_UP = dfUP[['CODPROD', 'PL', 'PONTO', 'CATEGORIA','V_CAP']].to_dict(orient='records')

    dfDOWN = dados.loc[(dados['V_CAP'] == 'DIV_DOWN') & (dados['FREQ_PROD'] == 2) & (dados['CATEGORIA'] != 'PEDENCIA')].copy()
    dfDOWN['PONTO'] = round(dfDOWN['PL'] * 0.3, 0).astype(int)
    dfDOWN = dfDOWN.drop_duplicates(subset=['CODPROD'], keep='first')
    lista_DOWN = dfDOWN[['CODPROD', 'PL_LASTRO', 'PONTO','CATEGORIA','V_CAP']].to_dict(orient='records')    
    
    contagemUP = dfUP['CODPROD'].nunique()
    contagemDOWN = dfDOWN['CODPROD'].nunique()
    print(f">> Encontrados no DFUP: {contagemUP} item(s)")
    print(f">> Encontrados no DFDOWN: {contagemDOWN} item(s)")
    

    print("\n=================== SELEÇÃO DE MODALIDADE ===================")
    print(" 1 - 'DF_UP' (Usará PL) | 2 - 'DF_DOWN' (Usará PL_LASTRO)")
    print("=============================================================")
    while True:
        escolha = int(input("Digite a opção desejada (1 ou 2): ").strip())
        
        if escolha == 1:
            capacidade = 'PL'
            listaMOD = lista_UP
            break
        elif escolha == 2:
            capacidade = 'PL_LASTRO'
            listaMOD = lista_DOWN
            break
        else:
            print("[ALERTA] Opção inválida! Digite estritamente 1 ou 2.")
    
except Exception as e:
    with open(r"c:\Users\wesley.oliveira\WS_OLIVEIRA\SCRIPTS\log_erros.txt", "a", encoding="utf-8") as f:
        f.write(f"Erro na etapa de dados: {str(e)}\n")
    print(f"\n[ERRO CRÍTICO] Houve um erro na etapa de dados: {e}")
    listaMOD = []

# --- ETAPA 2: AUTOMAÇÃO ---
try:
    listaFora = {"Produto": None, "CATEGORIA": None}
    limpar_terminal()
    
    print("="*60)
    print(f">> TOTAL DE REGISTROS A PROCESSAR: {len(listaMOD)}")
    print("="*60 + "\n")
    
    trava = 0.1
    if listaMOD:
        input(" -> Prepare a tela do sistema e pressione [ENTER] para continuar...")
        print("\n[ATENÇÃO] Clique AGORA no primeiro campo onde a digitação deve iniciar!\n")            
        
        for segundos_restantes in range(5, 0, -1):    
            print(f"\rIniciando disparos em {segundos_restantes}s... NÃO MEXA NO MOUSE OU TECLADO!", end="", flush=True)          
            pag.sleep(1.0)

        print("\n\n[STATUS] Automação em andamento...")
        total = len(listaMOD)
        for fase, registro in enumerate(listaMOD, 1):           
            # Campo 1: Código do Produto
            Verificarcopy(registro['CODPROD'])
            pag.press('enter')
            pag.sleep(trava)

            # Retorna X campos usando Shift+Tab dependendo da Categoria
            if registro['CATEGORIA'] == 'VAZIO':
                var = 7
            elif registro['CATEGORIA'] == 'OCUPADO': 
                var = 6
            elif registro['CATEGORIA'] == 'PEDENCIA': 
                listaFora["Produto"] = registro['CODPROD']
                listaFora["CATEGORIA"] = 'PEDENCIA'
                continue    
            
            for _ in range(var):
                pag.hotkey("shift", "tab")
                pag.sleep(trava)

            # Campo 2: Capacidade
            Verificarcopy(registro[capacidade])
            pag.press('enter')
            pag.sleep(trava)

            # Campo 3: Ponto de Reposição
            Verificarcopy(registro['PONTO'])

            pag.press('enter')
            pag.press('enter')
            pag.press('enter')
            pag.sleep(trava)

            print(f"\rProgresso: [{fase}/{total}] - Itens restantes: {total - fase} ", end="", flush=True)
    else:
        print("[AVISO] Nenhum registro válido encontrado para esta modalidade.")

except Exception as e:
    with open(r"c:\Users\wesley.oliveira\WS_OLIVEIRA\SCRIPTS\log_erros.txt", "a", encoding="utf-8") as f:
        f.write(f"Erro na etapa de automação: {str(e)}\n")
    print(f"\n\n[ERRO] Falha durante a execução dos cliques: {e}")

print("\n\n" + "="*60)
print("[SUCESSO] O script finalizou as tentativas de processamento.")
print("="*60)
input("\nPressione [ENTER] para fechar esta janela com segurança...")