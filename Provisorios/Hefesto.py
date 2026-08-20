import BOT3706, BOT3707, BOT1755
import os
import time
import pandas as pd 

class auxiliar:
    @staticmethod
    def CapturarFile():
        nomeFile = 'ProvisorioFile.xlsx'
        pasta_script = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(pasta_script, nomeFile)

    @staticmethod
    def limpar_terminal():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def AbrirFile():
        caminho = auxiliar.CapturarFile()
        if os.path.exists(caminho):
            os.startfile(caminho)
        else:
            etapas = {
                        'transferencia': ["CODPROD"],
                        "Retirada": ['CODPROD', 'DTULTENT', 'QTESTGER', 'OBSFL'],
                        'transf3707': ["CODPROD", "DESTINO"],
                        'Etapa_3': ["CODPROD", "PL_LASTRO", "PL", "CAP", "QTEnd", "V_CAP"]
                    }

            with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
                for nome_aba, colunas in etapas.items():
                    pd.DataFrame(columns=colunas).to_excel(writer, sheet_name=nome_aba, index=False)

            os.startfile(caminho)  

    @staticmethod  
    def FecharFile():
        caminho = auxiliar.CapturarFile()

        if os.path.exists(caminho):
            try:
                os.remove(caminho)
                print("Arquivo antigo removido com sucesso.")
                return True
            except PermissionError:
                print("Erro: O arquivo está aberto no Excel. Feche o arquivo antes de continuar.")
                input("[enter] para continuar...")
                return False
        return True

def main():
    while True:
        auxiliar.limpar_terminal()
        auxiliar.AbrirFile()

        largura = 71

        print("=" * largura)
        print("Central de automação".center(largura))
        print("=" * largura + "\n")
        print("Escolha uma das opções abaixo:")
        print("1. Retirada de Endereços         [3706]")
        print("2. Ajuste de Capacidade          [3706]")
        print("3. Transferência de Endereços    [3707]")
        print("4. Finalização de o.s            [1755]")
        print("0. Sair\n")
        print("-" * largura)
        try:
            escolha = int(input(">> ").strip())
        except ValueError:
            print("[ALERTA] Por favor, digite apenas números!")
            time.sleep(1)
            continue

        match escolha:
            case 1:
                BOT3706.RetirarEndereco(auxiliar.CapturarFile())
            case 2:
                BOT3706.ProcessarCapacidade(largura)
            case 3: 
                BOT3707.TransferirPROD(auxiliar.CapturarFile())
            case 4:
                BOT1755.FinalizarOS()
            case 0:
                print("Encerrando Hefesto...")
                if os.path.exists(auxiliar.CapturarFile()):
                    sucesso_fechamento = auxiliar.FecharFile()
                    if sucesso_fechamento:
                        time.sleep(0.5)
                        break
                    
            case _:
                print("[ALERTA] Opção inválida! Digite uma das alternativa acima")
                time.sleep(1)
                continue
            
if __name__ == "__main__":
    main()