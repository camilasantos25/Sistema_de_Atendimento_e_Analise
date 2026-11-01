import os
import tempfile
import unittest
from datetime import datetime
from persistencia.armazenamento import carregar_sistema, salvar_sistema
from persistencia.exportacao import gravar_csv
from servicos.registro import configurar_logs, encerrar_logs
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes

def hora(dia, horas, minutos):
    return datetime(2026, 10, dia, horas, minutos, 0)

def mensagens(capturado):
    resultado = []
    for registro in capturado.records:
        resultado.append(registro.getMessage())
    return resultado

class TestLogsDosAtendimentos(unittest.TestCase):
    def setUp(self):
        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.servico = ServicoAtendimentos(self.clientes, self.atendentes)
        self.clientes.cadastrar(1, "Ana", "11999990000", 0, hora(1, 9, 0))
        self.atendentes.cadastrar(1, "Carla")

    def test_abrir_registra_so_ids(self):
        with self.assertLogs("atendimento", level="INFO") as capturado:
            self.servico.abrir(1, hora(1, 10, 0))

        self.assertEqual(
            mensagens(capturado),
            ["Atendimento 1 aberto: cliente 1, prioridade 0"],
        )
        self.assertNotIn("Ana", mensagens(capturado)[0])
        self.assertNotIn("11999990000", mensagens(capturado)[0])

    def test_chamar_registra(self):
        self.servico.abrir(1, hora(1, 10, 0))

        with self.assertLogs("atendimento", level="INFO") as capturado:
            self.servico.chamar_proximo(1, hora(1, 10, 0))

        self.assertEqual(
            mensagens(capturado),
            ["Atendimento 1 chamado: atendente 1 atende o cliente 1"],
        )

    def test_finalizar_registra_a_duracao(self):
        self.servico.abrir(1, hora(1, 10, 0))
        self.servico.chamar_proximo(1, hora(1, 10, 0))

        with self.assertLogs("atendimento", level="INFO") as capturado:
            self.servico.finalizar(1, hora(1, 10, 5))

        self.assertEqual(
            mensagens(capturado),
            ["Atendimento 1 finalizado: atendente 1, cliente 1, duração 300.0 segundos"],
        )

    def test_desfazer_registra(self):
        self.servico.abrir(1, hora(1, 10, 0))
        self.servico.chamar_proximo(1, hora(1, 10, 0))
        self.servico.finalizar(1, hora(1, 10, 5))

        with self.assertLogs("atendimento", level="INFO") as capturado:
            self.servico.desfazer_finalizacao()

        self.assertEqual(
            mensagens(capturado),
            ["Finalização do atendimento 1 desfeita: atendente 1 voltou a atender o cliente 1"],
        )

    def test_remover_cliente_registra(self):
        with self.assertLogs("atendimento", level="INFO") as capturado:
            self.servico.remover_cliente(1)

        self.assertEqual(mensagens(capturado), ["Cliente 1 removido"])

    def test_remover_inativos_registra_a_quantidade(self):
        with self.assertLogs("atendimento", level="INFO") as capturado:
            self.servico.remover_clientes_inativos(10, hora(28, 10, 0))

        self.assertEqual(
            mensagens(capturado),
            ["Remoção de inativos: 1 cliente(s) removido(s) (limite de 10 dias)"],
        )

    def test_operacoes_recusadas_nao_registram(self):
        with self.assertNoLogs("atendimento", level="INFO"):
            with self.assertRaises(ValueError):
                self.servico.abrir(99)
            with self.assertRaises(ValueError):
                self.servico.chamar_proximo(1)
            with self.assertRaises(ValueError):
                self.servico.finalizar(1)
            with self.assertRaises(ValueError):
                self.servico.desfazer_finalizacao()
            with self.assertRaises(ValueError):
                self.servico.remover_cliente(99)

class TestLogsDaPersistencia(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.pasta.cleanup()

    def test_salvar_registra_as_quantidades(self):
        clientes = ServicoClientes()
        atendentes = ServicoAtendentes()
        atendimentos = ServicoAtendimentos(clientes, atendentes)
        clientes.cadastrar(1, "Ana", "11999990000", 0, hora(1, 9, 0))
        atendentes.cadastrar(1, "Carla")
        atendimentos.abrir(1, hora(1, 10, 0))

        with self.assertLogs("atendimento", level="INFO") as capturado:
            salvar_sistema(self.pasta.name, clientes, atendentes, atendimentos)

        self.assertEqual(len(capturado.records), 1)
        mensagem = mensagens(capturado)[0]
        self.assertIn("Sistema salvo em", mensagem)
        self.assertIn("1 clientes, 1 atendentes, 1 atendimentos", mensagem)

    def test_carregar_registra_avisos_como_warning_e_o_resumo_como_info(self):
        gravar_csv(
            os.path.join(self.pasta.name, "clientes.csv"),
            ["id", "nome", "telefone", "prioridade", "ultima_atividade"],
            [
                ["0", "Zero", "11999990000", "0", "2026-10-01T09:00:00"],
                ["1", "Ana", "11999990001", "0", "2026-10-01T09:00:00"],
            ],
        )

        with self.assertLogs("atendimento", level="INFO") as capturado:
            carregar_sistema(self.pasta.name)

        self.assertEqual(len(capturado.records), 2)
        self.assertEqual(capturado.records[0].levelname, "WARNING")
        self.assertIn("linha 2", capturado.records[0].getMessage())
        self.assertEqual(capturado.records[1].levelname, "INFO")
        self.assertIn(
            "1 clientes, 0 atendentes, 1 avisos",
            capturado.records[1].getMessage(),
        )

class TestArquivoDeLog(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "logs", "sistema.log")

        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.servico = ServicoAtendimentos(self.clientes, self.atendentes)
        self.clientes.cadastrar(1, "Ana", "11999990000", 0, hora(1, 9, 0))
        self.clientes.cadastrar(2, "Davi", "11999990001", 0, hora(1, 9, 0))

    def tearDown(self):
        encerrar_logs()
        self.pasta.cleanup()

    def linhas_do_arquivo(self):
        encerrar_logs()
        with open(self.caminho, "r", encoding="utf-8") as arquivo:
            return arquivo.read().splitlines()

    def test_cria_a_pasta_e_grava_no_formato_combinado(self):
        configurar_logs(self.caminho)
        self.servico.abrir(1, hora(1, 10, 0))

        linhas = self.linhas_do_arquivo()
        self.assertEqual(len(linhas), 1)
        self.assertIn(" | INFO | Atendimento 1 aberto: cliente 1, prioridade 0", linhas[0])

    def test_configurar_duas_vezes_nao_duplica_as_linhas(self):
        configurar_logs(self.caminho)
        configurar_logs(self.caminho)
        self.servico.abrir(1, hora(1, 10, 0))

        self.assertEqual(len(self.linhas_do_arquivo()), 1)

    def test_logs_acumulam_entre_execucoes(self):
        configurar_logs(self.caminho)
        self.servico.abrir(1, hora(1, 10, 0))
        encerrar_logs()

        configurar_logs(self.caminho)
        self.servico.abrir(2, hora(1, 10, 5))

        linhas = self.linhas_do_arquivo()
        self.assertEqual(len(linhas), 2)
        self.assertIn("cliente 1", linhas[0])
        self.assertIn("cliente 2", linhas[1])

    def test_depois_de_encerrar_nao_grava_mais(self):
        configurar_logs(self.caminho)
        encerrar_logs()
        self.servico.abrir(1, hora(1, 10, 0))

        self.assertEqual(self.linhas_do_arquivo(), [])