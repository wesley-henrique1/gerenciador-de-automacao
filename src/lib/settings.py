import sys
import os 

class __auxiliares__:
    if getattr(sys, "frozen", False):
        Diretorio = os.path.dirname(sys.executable)
        Estatico = sys._MEIPASS
    else:
        PastaAtual = os.path.dirname(os.path.abspath(__file__))
        PastaModulos = os.path.dirname(PastaAtual)
        Diretorio = os.path.dirname(PastaModulos)

    DataBase = os.path.join(Diretorio, "database")
    OutPut = os.path.join(Diretorio, "output")
    source = os.path.join(Diretorio, 'src')

class _Source(__auxiliares__):
    Diretorio = __auxiliares__.source

    assets = os.path.join(Diretorio, "assets")
    Library = os.path.join(Diretorio, 'lib')
    Modulos = os.path.join(Diretorio, 'mod')
    Views = os.path.join(Diretorio, 'views')


    pass
class Assets(_Source):
    Diretorio = _Source.assets
    Icons = os.path.join(Diretorio, "icon")
    Imagens = os.path.join(Diretorio, "img")
    Jsons = os.path.join(Diretorio, "json")
    Videos = os.path.join(Diretorio, "video")

    "Pasta dos icones"
    IcoCorte = os.path.join(Icons, 'Corte.ico')
    IcoEngrenagem = os.path.join(Icons, 'engrenagem.ico')
    IcoPrincipal = os.path.join(Icons, 'FleshPrincipal.ico')

    "Pasta das imagens"
    ImgBackHorizontal = os.path.join(Imagens, 'BackHorizontal.png')
    ImgBackVertical = os.path.join(Imagens, 'BackVertical.png')
    ImgEngrenagem = os.path.join(Imagens, 'engrenagem.png')
    ImgPrincipal = os.path.join(Imagens, 'FleshPerfil.png')

    "Pasta dos jsons"
    JsonFlowRack = os.path.join(Jsons, 'FlowRack.json')
    JsonJornada = os.path.join(Jsons, 'jornada.json')
    JsonLogTime = os.path.join(Jsons, 'logTime.json')
    JsonModulo = os.path.join(Jsons, 'modulo.json')
    JsonRotina = os.path.join(Jsons, 'rotinas.json')
    JsonErros = os.path.join(Jsons, 'ValError.json')
    pass

"Pasta da base de dados dividido por modulos do WINTHOR"
class Filial_18(__auxiliares__):
    _8596 = os.path.join(__auxiliares__.DataBase, '8596 - Dados filial_18.xlsx')
    _286 = os.path.join(__auxiliares__.DataBase, '0286 - Consultar filial_18.xls')
    
    pass
class Gestao(__auxiliares__):
    Corte = r'z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.1.1 Analise de Cortes\2026\# 2 Acompanhamento de produtos cortados.xlsx'
    CheioVazio = r'z:\1 - CD Dia\4 - Equipe PCL\6.1 - Inteligência Logística\6.1.5 - Relatório Cheio x vazio\RETORNO'
    invCont = None

    _001 = os.path.join(__auxiliares__.DataBase, '001 - TOTVS_LIFE.xlsx')
    _105 = os.path.join(__auxiliares__.DataBase, '0105 - Posição do estoque.xls')
    _286 = os.path.join(__auxiliares__.DataBase, '0286 - Consultar Produtos.xls')
    _718 = os.path.join(__auxiliares__.DataBase, '0718 - Contas pagas.xls')
    _1118 = os.path.join(__auxiliares__.DataBase, '1118 - Gerencial 11.xls')

    MalhaFina_day = os.path.join(__auxiliares__.DataBase, 'CD MATRIZ - Malha Fina 112025.xlsx')
    MalhaFina_mes = os.path.join(__auxiliares__.DataBase, 'CD MATRIZ - Malha Fina até 6 meses.xlsx')
    pass
class Relatorios(__auxiliares__):
    _8041 = os.path.join(__auxiliares__.DataBase, '8041 - Relatorio de picking master.xlsx')
    _8132 = os.path.join(__auxiliares__.DataBase, '8132 - Relatorio de endereçamento.xlsx')
    _8134 = os.path.join(__auxiliares__.DataBase, '8134 - Analitico avaria.xlsx')
    _8560 = os.path.join(__auxiliares__.DataBase, '8560 - Relatório acesso.xlsx')
    _8573 = os.path.join(__auxiliares__.DataBase, '8573 - Emissão etiquetas cod. barras.xlsx')
    _8576 = os.path.join(__auxiliares__.DataBase, '8576 - Acompanhamento de anomalias.xlsx')
    _8596 = os.path.join(__auxiliares__.DataBase, '8596 - Dados logistico produtos WMS.xlsx')
    _8611 = os.path.join(__auxiliares__.DataBase, '8611 - Responsável por gerar o.xlsx')
    _8628 = os.path.join(__auxiliares__.DataBase, '8628 - Relatorio de abastecimento.xlsx')
    _8664 = os.path.join(__auxiliares__.DataBase, '8664 - Eficiência do recebimento.xlsx')
    _8668 = os.path.join(__auxiliares__.DataBase, '8668 - Produtos Aereo x Picking.xlsx')

    pass
class Wms(__auxiliares__):
    _1702 = os.path.join(__auxiliares__.DataBase, '1702 - Cadastro de Endereços.txt')
    _1733 = os.path.join(__auxiliares__.DataBase, '1733 - Gestão de inventario.xls')
    _1767 = os.path.join(__auxiliares__.DataBase, '1767 - Relatorio de corte.txt')
    _1782 = os.path.join(__auxiliares__.DataBase, '1782 - Relatório de curva ABC de produtos.xls')

    validade07 = os.path.join(__auxiliares__.DataBase, '1707 - Consultar Validade.csv')
    gerencial07 = os.path.join(__auxiliares__.DataBase, '1707 - Estoque endereçado x Gerencial.txt')
    endereco07 = os.path.join(__auxiliares__.DataBase, '1707 - Relatório de produtos por endereços.txt')
    geral07 = os.path.join(__auxiliares__.DataBase, '1707 - Relatório geral.txt')

    pass
class BaseDados(__auxiliares__):
    _1782 = os.path.join(__auxiliares__.DataBase, 'BASE_1782')
    _8041 = os.path.join(__auxiliares__.DataBase, 'BASE_8041')
    _8668 = os.path.join(__auxiliares__.DataBase, 'BASE_8668')
    BaseFixa = os.path.join(__auxiliares__.DataBase, 'BASE_FIXAR')

    EndFixo = os.path.join(BaseFixa, 'BASE_ENDEREÇOS.xlsx')
    Func = os.path.join(BaseFixa, 'BASE_FUNCIONARIO.xlsx')

    path_acumulado = os.path.join(BaseFixa, "DB_ACUMULADO.accdb")
    drive = '{Microsoft Access Driver (*.mdb, *.accdb)}'

    DBVzCh = "DB_VAZIO_CHEIO"
    DBPedidos = "DB_PEDIDOS"
    DBProd = "DB_INVPROD"
    DBCont = "DB_INVCONT"
    pass

class OutPut(__auxiliares__):
    BotSave = os.path.join(__auxiliares__.OutPut, 'Retorno_BOT.xlsx')
    Baixas = os.path.join(__auxiliares__.OutPut, 'Analitico baixa.xlsx')
    Cadastro = os.path.join(__auxiliares__.OutPut, 'Analitico cadastro.xlsx')
    Corte = os.path.join(__auxiliares__.OutPut, 'Analitico corte.xlsx')
    GiroStatus = os.path.join(__auxiliares__.OutPut, 'Giro_Status.xlsx')
    MapaEstoque = os.path.join(__auxiliares__.OutPut, 'mapa_estoque.xlsx')

    Acuracidade = os.path.join(__auxiliares__.OutPut, 'BI_Acuracidade.xlsx')
    Abastecimento = os.path.join(__auxiliares__.OutPut, 'BI_ABASTECIMENTO.xlsx')
    
    Jupyter_1 = os.path.join(__auxiliares__.OutPut, 'JUPYTER_1.xlsx')
    Jupyter_2 = os.path.join(__auxiliares__.OutPut, 'JUPYTER_2.xlsx')

    P_Acuracidade = os.path.join(__auxiliares__.OutPut, 'BI_ACURACIDADE')

    Fefo8668 = r"z:\1 - CD Dia\4 - Equipe PCL\6.6 - Recuperação e Indenizado\6.6.3 - FEFO Validade\Curva A-B-C-D\Auditoria\FEFO_8668.xlsx"
    Fefo8628 = r"z:\1 - CD Dia\4 - Equipe PCL\6.6 - Recuperação e Indenizado\6.6.3 - FEFO Validade\Curva A-B-C-D\Auditoria\FEFO_8628.xlsx"

    pass
class ColNames():
    _1767 = [
        'data'
        ,'n_car'
        ,'cod'
        ,'desc'
        ,'n_ped'
        ,'qtde_orig'
        ,'vl_orig'
        ,'rua'
        ,'predio'
        ,'apto'
        ,'estoque_dia'
        ,'qtde_corte'
        ,'vl_corte'
        ,'hr'
        ,'min'
        ,'motivo'
        ,'cod_fuc'
        ,'func'
    ]
    _0702 = [
        'FL'
        ,'COD_END'
        ,'DEP'
        ,'RUA'
        ,'PREDIO'
        ,'NIVEL'
        ,'APTO'
        ,'TIPO'
        ,'ROTATIVO'
        ,'BLOQ'
        ,'DISP.'
        ,'PALETE'
        ,'ESTRUTURA'
    ]
    Geral = [
        "COD_END"
        ,"RUA"
        ,"PREDIO"
        ,"NIVEL"
        ,"APTO"
        ,"STATUS"
        ,"CODPROD"
        ,"DESCRICAO"
        ,"DT_VALIDADE"
        ,"EMBALAGEM"
        ,"LASTRO"
        ,"CAMADA"
        ,"NORMA_PL"
        ,"CAP_"
        ,"SALTO"
        ,"REP_"
        ,"TIPO_END"
        ,"QTDE"
        ,"ENTRADA"
        ,"SAIDA"
        ,"DISP_"
    ]
    Gerencial = [
        'COD'
        ,'DESCRICAO'
        ,'DEP'
        ,'RUA'
        ,'PREDIO'
        ,'NIVEL'
        ,'APTO'
        ,'EMBALAGEM'
        ,'CAP'
        ,'P_REP'
        ,'QTDE_O.S'
        ,'PICKING'
        ,'PULMAO'
        ,'ENDERECO'
        ,'GERENCIAL'
    ]
    Endereco = [
        'COD_END'
        ,'PREDIO'
        ,'NIVEL'
        ,'APTO'
        ,'STATUS'
        ,'COD'
        ,'DESC'
        ,'DT_ENTRADA'
        ,'DT_VALIDADE'
        ,'EMB'
        ,'LASTRO'
        ,'CAMADA'
        ,'CAP'
        ,'TIPO_PK'
        ,'PL_END'
        ,'QTDE'
        ,'ENTRADA'
        ,'SAIDA'
        ,'DISP'
    ]
    Movimentar = [
        'COD'
        ,'DESC'
        ,'EMBALAGEM'
        ,'UNID'
        ,'MOVI'
        ,'%'
        ,'%_ACUM'
        ,'CLASSE'
    ]
    Sugestao = [
        'COD'
        ,'DESCRIÇÃO'
        ,'EMBALAGEM'
        ,'UNID.'
        ,'DEP'
        ,'RUA'
        ,'PREDIO'
        ,'NIVEL'
        ,'APTO'
        ,'MÊS 1'
        ,'MÊS 2'
        ,'MÊS 3'
        ,'TIPO'
        ,'CAP'
        ,'1 DIA'
        ,'COM FATOR'
        ,'VARIAÇÃO'
        ,'%'
    ]
    pass