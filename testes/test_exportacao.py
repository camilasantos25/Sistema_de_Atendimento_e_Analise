import csv
import os
import tempfile
import unittest
from datetime import datetime

from persistencia.exportacao import (
    exportar_alertas,
    exportar_atendimentos,
    exportar_tempo_medio,
    exportar_top_clientes,
    gravar_csv,
)
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes
from servicos.servico_relatorios import ServicoRelatorios

def hora(dia, horas, minutos):
    return datetime(2026, 10, dia, horas, minutos, 0)

def ler_csv(caminho):
    with open(caminho, "r", newline="", encoding="utf-8") as arquivo:
        return list(csv.reader(arquivo))

def ler_texto(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

class TestGravarCsv(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "saida.csv")

    def tearDown(self):
        self.pasta.cleanup()

    def test_cabecalho_e_linhas(self):
        gravar_csv(self.caminho, ["a", "b"], [[1, "x"], [2, "y"]])
        self.assertEqual(
            ler_csv(self.caminho),
            [["a", "b"], ["1", "x"], ["2", "y"]],
        )

    def test_somente_cabecalho_quando_nao_ha_linhas(self):
        gravar_csv(self.caminho, ["a", "b"], [])
        self.assertEqual(ler_csv(self.caminho), [["a", "b"]])

    def test_virgula_e_acento_no_texto(self):
        gravar_csv(self.caminho, ["nome", "obs"], [["Silva, João", "ação"]])
        self.assertEqual(
            ler_csv(self.caminho),
            [["nome", "obs"], ["Silva, João", "ação"]],
        )
        self.assertIn('"Silva, João"', ler_texto(self.caminho))

    def test_substitui_arquivo_existente(self):
        gravar_csv(self.caminho, ["a"], [[1], [2], [3]])
        gravar_csv(self.caminho, ["a"], [[9]])
        self.assertEqual(ler_csv(self.caminho), [["a"], ["9"]])

class TestExportarRelatorios(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "saida.csv")

        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.atendimentos = ServicoAtendimentos(self.clientes, self.atendentes)
        self.relatorios = ServicoRelatorios(self.atendimentos)

        self.clientes.cadastrar(1, "Ana", "11999990000", 0)
        self.clientes.cadastrar(2, "Davi", "11999990001", 0)
        self.clientes.cadastrar(3, "Eva", "11999990002", 2)
        self.atendentes.cadastrar(1, "Carla")
        self.atendentes.cadastrar(2, "Paulo")

    def tearDown(self):
        self.pasta.cleanup()

    def atender(self, id_cliente, dia, minuto_inicio, minuto_fim):
        self.atendimentos.abrir(id_cliente, hora(dia, 10, minuto_inicio))
        self.atendimentos.chamar_proximo(1, hora(dia, 10, minuto_inicio))
        self.atendimentos.finalizar(1, hora(dia, 10, minuto_fim))

    def test_tempo_medio_com_atendimentos(self):
        self.atender(1, 1, 0, 5)
        self.atender(2, 1, 10, 20)

        exportar_tempo_medio(
            self.caminho,
            self.relatorios.tempo_medio_segundos(),
            len(self.atendimentos.historico),
        )
        self.assertEqual(
            ler_csv(self.caminho),
            [["total_atendimentos", "tempo_medio_segundos"], ["2", "450.0"]],
        )

    def test_tempo_medio_sem_historico_deixa_o_campo_vazio(self):
        exportar_tempo_medio(
            self.caminho,
            self.relatorios.tempo_medio_segundos(),
            len(self.atendimentos.historico),
        )
        self.assertEqual(
            ler_csv(self.caminho),
            [["total_atendimentos", "tempo_medio_segundos"], ["0", ""]],
        )

    def test_top_clientes(self):
        self.atender(3, 1, 0, 5)
        self.atender(2, 1, 10, 15)
        self.atender(1, 1, 20, 25)
        self.atender(2, 1, 30, 35)

        exportar_top_clientes(self.caminho, self.relatorios.top_clientes())
        self.assertEqual(
            ler_csv(self.caminho),
            [
                ["posicao", "id_cliente", "nome_cliente", "total_atendimentos"],
                ["1", "2", "Davi", "2"],
                ["2", "1", "Ana", "1"],
                ["3", "3", "Eva", "1"],
            ],
        )

    def test_top_clientes_sem_historico_so_tem_cabecalho(self):
        exportar_top_clientes(self.caminho, self.relatorios.top_clientes())
        self.assertEqual(
            ler_csv(self.caminho),
            [["posicao", "id_cliente", "nome_cliente", "total_atendimentos"]],
        )

    def test_atendimentos(self):
        self.atender(1, 1, 0, 5)

        exportar_atendimentos(self.caminho, self.atendimentos.historico)
        linhas = ler_csv(self.caminho)

        self.assertEqual(
            linhas[0],
            [
                "id_atendimento", "id_cliente", "nome_cliente", "id_atendente",
                "nome_atendente", "data", "hora_entrada", "hora_inicio",
                "hora_fim", "espera_segundos", "duracao_segundos",
            ],
        )
        self.assertEqual(
            linhas[1],
            [
                "1", "1", "Ana", "1", "Carla", "2026-10-01",
                "2026-10-01T10:00:00", "2026-10-01T10:00:00",
                "2026-10-01T10:05:00", "0.0", "300.0",
            ],
        )
        self.assertEqual(len(linhas), 2)

    def test_atendimentos_lista_vazia(self):
        exportar_atendimentos(self.caminho, [])
        self.assertEqual(len(ler_csv(self.caminho)), 1)

    def test_alertas(self):
        self.atendimentos.abrir(1, hora(1, 10, 0))
        alertas = self.relatorios.alertas_de_espera(900, hora(1, 10, 30))

        exportar_alertas(self.caminho, alertas)
        self.assertEqual(
            ler_csv(self.caminho),
            [
                [
                    "id_atendimento", "id_cliente", "nome_cliente",
                    "prioridade", "hora_entrada", "espera_segundos",
                ],
                ["1", "1", "Ana", "0", "2026-10-01T10:00:00", "1800.0"],
            ],
        )