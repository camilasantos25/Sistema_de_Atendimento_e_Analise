import os
from persistencia.armazenamento import carregar_sistema, salvar_sistema
from servicos.servico_relatorios import ServicoRelatorios

class Sistema:
    def __init__(self, pasta_dados, pasta_exportacao=None):
        self.pasta_dados = pasta_dados
        if pasta_exportacao is None:    # NOVO: por padrão, dentro da pasta de dados
            pasta_exportacao = os.path.join(pasta_dados, "relatorios")
        self.pasta_exportacao = pasta_exportacao
        (
            self.clientes,
            self.atendentes,
            self.atendimentos,
            self.avisos,
        ) = carregar_sistema(pasta_dados)
        self.relatorios = ServicoRelatorios(self.atendimentos)

    def salvar(self):
        salvar_sistema(self.pasta_dados, self.clientes, self.atendentes, self.atendimentos)

    def caminho_de_exportacao(self, nome_arquivo):
        os.makedirs(self.pasta_exportacao, exist_ok=True)
        return os.path.join(self.pasta_exportacao, nome_arquivo)