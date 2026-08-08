import json
import datetime as dt
from .settings import Assets

class ValidarErros:
    _mapeamento_cache = None

    def __init__(self, e=None, etapa=None, fonte="ModuloExterno"):
        self.fonte = fonte
        self._carregar_mapeamento()

        if e is not None and etapa is not None:
            self.registrar_log(e, etapa)

    def _carregar_mapeamento(self):
        """Carrega o arquivo de erros apenas se ainda não tiver sido carregado."""
        if ValidarErros._mapeamento_cache is None:
            try:
                with open(Assets.JsonErros, 'r', encoding='utf-8') as var:
                    ValidarErros._mapeamento_cache = json.load(var)
            except Exception as err:
                print(f"Aviso: Não foi possível carregar o arquivo de erros JSON ({err}). Usando padrão.")
                ValidarErros._mapeamento_cache = {}

        self.mapeamento = ValidarErros._mapeamento_cache

    def registrar_log(self, e: Exception, etapa: str):
        largura = 77
        nome_do_erro = type(e).__name__
        
        msg_padrao = self.mapeamento.get("Exception", "Ocorreu um erro inesperado no sistema.")
        msg = self.mapeamento.get(nome_do_erro, msg_padrao)
        
        agora = dt.datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        log_conteudo = (
            f"{'='* largura}\n"
            f"FONTE: {self.fonte} | ETAPA: {etapa} | DATA: {agora}\n"
            f"TIPO: {nome_do_erro}\n"
            f"MENSAGEM: {msg}\n"
            f"DETALHE TÉCNICO: {e}\n"
            f"{'='* largura}\n\n"
        )
        caminho_log = getattr(Assets, 'PathLog', 'log_erros.txt')

        try:
            with open(caminho_log, "a", encoding="utf-8") as f:
                f.write(log_conteudo)
            print(f"Log gravado para a etapa: {etapa}")
        except Exception as erro_f:
            print(f"Falha crítica ao gravar log: {erro_f}")