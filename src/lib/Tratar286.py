import pandas as pd
from .valerros import ValidarErros

class BaseDados286:
    validador = ValidarErros(fonte="main_logica")
    def __init__(self):
        self.Ativos11 = r'z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.6 - PCL Cadastro\_BaseDados\286 - Estoque ATIVO11.xls'
        self.Ativos18 = r'z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.6 - PCL Cadastro\_BaseDados\286 - Estoque ATIVO18.xls'

        self.Fl11 = r'z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.6 - PCL Cadastro\_BaseDados\286 - Estoque FL11.xls'
        self.Fl18 = r'z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.6 - PCL Cadastro\_BaseDados\286 - Estoque FL18.xls'

        self.cols = ['Código', 'Descrição ', 'Estoque', 'Qtde Pedida', 'Bloqueado(Qt.Bloq.-Qt.Avaria)', 'Qt.Avaria']
        self.colunas = [
            'Estoque_x', 'Qtde Pedida_x', 'Bloqueado(Qt.Bloq.-Qt.Avaria)_x', 'Qt.Avaria_x',
            'Estoque_y', 'Qtde Pedida_y', 'Bloqueado(Qt.Bloq.-Qt.Avaria)_y', 'Qt.Avaria_y'
        ]
        self.ListaAR = [self.Ativos11, self.Ativos18, self.Fl11, self.Fl18]

    def __converter_numero_seguro(self, val):
        if isinstance(val, (int, float)):
            return float(val) if pd.notna(val) else 0.0
        
        val_str = str(val).strip()
        if val_str.lower() in ['nan', '', 'none']:
            return 0.0
        
        if ',' in val_str and '.' in val_str:
            val_str = val_str.replace('.', '').replace(',', '.')
        elif ',' in val_str:
            val_str = val_str.replace(',', '.')
        elif val_str.count('.') > 1:
            val_str = val_str.replace('.', '')
        try:
            return float(val_str)
        except ValueError:
            return 0.0

        except Exception as e:
            self.validador.registrar_log(e, "286_numeros")
            return False

    def Pipeline(self, colcheck= None):
        try:
            if colcheck:
                self.cols.extend(colcheck)

            DfAtivos11 = pd.read_excel(self.Ativos11, usecols=self.cols)
            DfAtivos18 = pd.read_excel(self.Ativos18, usecols=self.cols)

            DataFL11 = pd.read_excel(self.Fl11, usecols=self.cols)
            DataFL18 = pd.read_excel(self.Fl18, usecols=self.cols)

            for df in [DfAtivos11, DfAtivos18, DataFL11, DataFL18]:
                df['CODPROD'] = pd.to_numeric(df['Código'], errors='coerce')
                df.dropna(subset=['CODPROD'], inplace=True)
                df['CODPROD'] = df['CODPROD'].astype(int)

            DfEstoque11 = pd.concat([DfAtivos11, DataFL11], axis=0).drop_duplicates(subset=['CODPROD'])
            DfEstoque18 = pd.concat([DfAtivos18, DataFL18], axis=0).drop_duplicates(subset=['CODPROD'])

            DfEstoque = DfEstoque11.merge(DfEstoque18, on='CODPROD', how='left')

            for coluna in self.colunas:
                DfEstoque[coluna] = DfEstoque[coluna].apply(self.__converter_numero_seguro).fillna(0)
            
            DfEstoque['DESC'] = DfEstoque['Descrição _x'].combine_first(DfEstoque['Descrição _y'])

            DfEstoque['ESTOQUE'] = DfEstoque['Estoque_x'] + DfEstoque['Estoque_y']
            DfEstoque['PEDIDO'] = DfEstoque['Qtde Pedida_x'] + DfEstoque['Qtde Pedida_y']
            DfEstoque['BLOQUEADO'] = DfEstoque['Bloqueado(Qt.Bloq.-Qt.Avaria)_x'] + DfEstoque['Bloqueado(Qt.Bloq.-Qt.Avaria)_y'] 
            DfEstoque['AVARIA'] = DfEstoque['Qt.Avaria_x'] + DfEstoque['Qt.Avaria_y']

            DfEstoque['TOTALBLOQ'] = DfEstoque['BLOQUEADO'] + DfEstoque['AVARIA'] 
            DfEstoque['DISPONIVEL'] = DfEstoque['ESTOQUE'] - DfEstoque['TOTALBLOQ']

            cols_descarte = [c for c in self.colunas + ['Descrição _x', 'Descrição _y', 'Código_x', 'Código_y'] if c in DfEstoque.columns]
            DfEstoque = DfEstoque.drop(columns=cols_descarte)

            return DfEstoque

        except Exception as e:
            self.validador.registrar_log(e, "Extract")
            return False
    def RetornoBase(self):
        return self.ListaAR 
