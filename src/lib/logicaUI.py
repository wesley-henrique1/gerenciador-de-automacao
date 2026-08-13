import threading
from .valerros import ValidarErros

class Processador:
    validador = ValidarErros(fonte="main_logica")

    def __init__(self, UI):
        self._widget_ancora = UI

    def _executar_na_main_thread(self, func, *args, **kwargs):
        self._widget_ancora.retorno.after(0, lambda: func(*args, **kwargs))
    def _alterar_estado_botoes(self, estado):
        self._widget_ancora.bt_iniciar.config(state=estado)
        self._widget_ancora.bt_limpar.config(state=estado)
        pass
    def _atualizar_contador(self, texto):
        self._widget_ancora.contador.config(text=texto)
        pass
    def _inserir_texto_no_widget(self, widget, conteudo, limpar=True):
        widget.config(state="normal")
        if limpar:
            widget.delete("1.0", "end")
        widget.insert("end", conteudo)
        widget.config(state="disabled")
        widget.see("end")
        pass    
    def _processar_finalizacao(self, lista_de_logs, lista_de_file, listaSaida, dic_log, log_data, msg_corte):
        """Centraliza o encerramento do processo e distribui as atualizações para as respectivas telas."""
        try:       
            logs_unicos = list({log['ARQUIVO']: log for log in lista_de_logs if isinstance(log, dict)}.values())
            logs_file = list({log['MODULO']: log for log in lista_de_file if isinstance(log, dict)}.values())
            logs_saida = list({log['ARQUIVO']: log for log in listaSaida if isinstance(log, dict)}.values())
            
            def acoes_finais_ui():
                self._atualizar_logs(logs_unicos)
                self._atualizar_db(logs_file)
                self._atualizar_output(logs_saida)
                
                self._widget_ancora.ancoragemPanel(dic_log)
                
                if msg_corte is not None:
                    self._widget_ancora.tela_CORTE("Relatório de Corte", msg_corte)
                
                self._alterar_estado_botoes("normal")

            self._executar_na_main_thread(acoes_finais_ui)

        except Exception as e:
            self.validador.registrar_log(e, "TASK_RETORNO")

    def _atualizar_logs(self, dados_arquivos):
        """Tela 1: Formata e renderiza exclusivamente a tabela de arquivos em self._widget_ancora.retorno"""
        try:
            if not dados_arquivos:
                self._widget_ancora._exibir_mensagem_status(" >>> NENHUM ARQUIVO PROCESSADO")
                return
            titulos = f"{"ARQUIVOS":^46} | {'DATA':^12} | {'HORA':^8}\n"
            linha = f"{'-' * 74}\n"
            conteudo = titulos + linha

            for item in dados_arquivos:
                nome_arq = str(item.get('ARQUIVO', 'DESCONHECIDO'))
                nome_arq = nome_arq[:43] + "..." if len(nome_arq) > 43 else nome_arq
                
                date = item.get('DATA', '--/--/----')
                hrs = item.get('HORAS', '--:--')
                
                conteudo += f"{nome_arq:<46} | {date:<12} | {hrs:<8}\n"

            self._inserir_texto_no_widget(self._widget_ancora.retorno, conteudo, limpar=True)
        except Exception as e:
            self.validador.registrar_log(e, "Atualizar LOG Arquivos")
            self._widget_ancora._exibir_mensagem_status(" >>> ERRO AO GERAR LOG DE ARQUIVOS.")
        pass
    def _atualizar_db(self, dados_modulos):
        if not dados_modulos:
            return      
        try:
            titulos = f"{'MODULO':^15} | {'ARQUIVOS':^8} | {'ERROS':^5} | {'LEITURAS':^9}\n"
            linha = f"{"-" * 45}\n"
            conteudo = titulos + linha
            
            for file in dados_modulos:
                modulo = file.get("MODULO", "DESCONHECIDO")
                contador = file.get("ARQUIVOS", 0)
                fora = file.get("ERROS", 0)
                qtde = file.get("LEITURA", 0)
                
                conteudo += f"{modulo:^15} | {contador:^8} | {fora:^5} | {qtde:^9}\n"

            self._inserir_texto_no_widget(self._widget_ancora.retorno_db, conteudo, limpar=True)
        except Exception as e:
            self.validador.registrar_log(e, "Atualizar LOG Banco de Dados")
        pass
    def _atualizar_output(self, dados_saida):
        if not dados_saida:
            return
        try:
            titulos = f"{'ARQUIVO':^24} | {'DATA':^10} | {'HORA':^8}\n"
            linha = f"{'-' * 48}\n"
            conteudo = titulos + linha
            for var in dados_saida:
                modulo = var.get("ARQUIVO", "DESCONHECIDO")
                date = var.get('DATA', '--/--/----')
                hrs = var.get('HORA', '--:--')

                conteudo += f"{modulo:<24} | {date:^10} | {hrs:^8}\n"

            self._inserir_texto_no_widget(self._widget_ancora.retorno_file, conteudo, limpar=True)
        except Exception as e:
            self.validador.registrar_log(e, "Atualizar Output Dados")

    def task_workflow(self, argumento):
        msg_corte = None
        log_data = None

        lista_de_logs = []
        lista_de_file = []
        listaSaida = []
        dicFilanizar = {}
        
        total_scripts = len(argumento)

        if total_scripts == 0:
            self._executar_na_main_thread(self._atualizar_contador, "PROGRESSO >> 0% || 0/0 OPERAÇÃO")
            self._executar_na_main_thread(self._alterar_estado_botoes, "normal")
            return

        for i, nome in enumerate(argumento):
            try:
                progresso_anterior = (i / total_scripts) * 100
                txt_progresso = f"PROGRESSO >> {progresso_anterior:.0f}% -> {nome} || {i}/{total_scripts} OPERAÇÃO"
                self._executar_na_main_thread(self._atualizar_contador, txt_progresso)

                classe_do_script = self._widget_ancora.scripts_map[nome]
                instancia = classe_do_script()

                if nome == "abstKeys":
                    status_pipeline, log_data = instancia.pipeline() 
                else:
                    status_pipeline = instancia.pipeline()
                
                log_arquivo, log_db = instancia.carregamento(status_pipeline)
                logOut, path = instancia.outputLog(status_pipeline)
                dados_arquivo = logOut[0]
                
                if nome == "CorteKeys" and status_pipeline is not False:
                    msg_corte = instancia.Log_Retorno()

                dicFilanizar[nome] = {
                    "estado": "Executado" if status_pipeline else "Travado (Erro Interno)"
                    ,"nomeclatura": dados_arquivo["ARQUIVO"]
                    ,"path": path
                }
                if log_arquivo:
                    lista_de_logs.extend(log_arquivo if isinstance(log_arquivo, list) else [log_arquivo])
                if log_db:
                    lista_de_file.extend(log_db if isinstance(log_db, list) else [log_db])
                if logOut:
                    listaSaida.extend(logOut if isinstance(logOut, list) else [logOut])

                progresso_atual = ((i + 1) / total_scripts) * 100
                txt_final = f"PROGRESSO >> {progresso_atual:.0f}% -> {nome} || {i + 1}/{total_scripts} OPERAÇÃO"
                self._executar_na_main_thread(self._atualizar_contador, txt_final)

            except Exception as e:
                self.validador.registrar_log(e, f"Módulo: {nome}")
                self._executar_na_main_thread(self._widget_ancora._exibir_mensagem_status," >>> ERRO AO GERAR LOG. VERIFIQUE log_erros.txt"
                )

        self._processar_finalizacao(
            lista_de_logs= lista_de_logs
            ,lista_de_file= lista_de_file
            ,listaSaida= listaSaida
            ,dic_log= dicFilanizar
            ,log_data=log_data
            ,msg_corte= msg_corte
        )
    def executar_threads(self, selecionados):
        self._alterar_estado_botoes("disabled")
        thread = threading.Thread(
            target=self.task_workflow, 
            args=(selecionados,), 
            daemon=True
        )
        thread.start()