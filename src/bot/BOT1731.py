from lib.settings import ColNames, OutPut, Wms

import os
from datetime import datetime
import numpy as np
import pandas as pd
import pyautogui as pag
import pyperclip as pc


class auxiliar:
    pass

class TransfINV:
    def __init__(self):
        pass

    def __Simulador(self, df: pd.DataFrame):
        pass

    def __pipeline(self, listaPath: list[str], listaSave: list[str]):
        try:
            pass
        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
        try:
            pass
        except Exception as e:
            self.validador.registrar_log(e, "Transform")
            return False
        try:
            return True
        except Exception as e:
            self.validador.registrar_log(e, "Load")
            return False

    def ExecutarBot(self, listaPath: list[str], listaSave: list[str]):
        pass
