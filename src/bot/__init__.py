import importlib.util
import json
import sys
import os

from ..lib.settings import Assets
from ..lib import ValidarErros

# from lib.settings import Assets
# from lib import ValidarErros

def ExeBots():
    validador = ValidarErros(fonte="bot")
    base = Assets.JsonBot

    if getattr(sys, 'frozen', False):
        root_dir = os.path.dirname(sys.executable)
    else:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    with open(base, 'r', encoding= 'utf-8') as var:
        Modular = json.load(var)
    listKeys = []
    dicModular = {}

    for var in Modular.keys():
        listKeys.append(var)

    for var in listKeys:
        try:
            if Modular[var]['Booleano'] == 'True':
                ChaveModulo = var
                NomeModulo = Modular[var]['NameFile']
                NomeClasse = Modular[var]['Logic']
                NomeClatura = Modular[var]['NameBT']


                # 1. Monta o caminho exato do arquivo .py na pasta física externa
                caminho_modulo = os.path.join(root_dir, "src", "bot", f"{NomeModulo}.py")
                
                # 2. Carrega o arquivo .py diretamente do disco de forma 100% dinâmica
                spec = importlib.util.spec_from_file_location(f"src.bot.{NomeModulo}", caminho_modulo)
                modulo_carregado = importlib.util.module_from_spec(spec)
                
                # Registra no sys.modules para manter a arquitetura interna idêntica
                sys.modules[f"src.bot.{NomeModulo}"] = modulo_carregado
                spec.loader.exec_module(modulo_carregado)
                
                # 3. Busca a classe dentro do módulo recém-carregado
                ClasseFisica = getattr(modulo_carregado, NomeClasse)        
                dicModular[ChaveModulo] = {
                    "Classe": ClasseFisica,
                    "Nome": NomeClatura
                }
        except Exception as e:
            validador.registrar_log(e, "_init_")
    return dicModular