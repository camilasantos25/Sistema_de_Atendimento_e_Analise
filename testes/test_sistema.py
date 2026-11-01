import os
import tempfile
import unittest
from interface.sistema import Sistema
from persistencia.exportacao import gravar_csv

class TestSistema(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.pasta.cleanup()

    def test_pasta_inexistente_comeca_vazio(self):
        sistema = Sistema(os.path.join(self.pasta.name, "dados"))
        self.assertEqual(sistema.clientes.total(), 0)
        self.assertEqual(sistema.atendentes.total(), 0)
        self.assertEqual(sistema.avisos, [])

    def test_salvar_e_abrir_de_novo(self):
        sistema = Sistema(self.pasta.name)
        sistema.clientes.cadastrar(1, "Ana", "11999990000", 0)
        sistema.atendentes.cadastrar(1, "Carla")
        sistema.salvar()

        novo = Sistema(self.pasta.name)
        self.assertEqual(novo.clientes.buscar(1).nome, "Ana")
        self.assertEqual(novo.atendentes.buscar(1).nome, "Carla")

    def test_relatorios_usam_os_mesmos_atendimentos(self):
        sistema = Sistema(self.pasta.name)
        self.assertIs(sistema.relatorios.servico_atendimentos, sistema.atendimentos)

    def test_linhas_ruins_do_arquivo_viram_avisos(self):
        gravar_csv(
            os.path.join(self.pasta.name, "clientes.csv"),
            ["id", "nome", "telefone", "prioridade", "ultima_atividade"],
            [["0", "Zero", "11999990000", "0", "2026-10-01T09:00:00"]],
        )
        sistema = Sistema(self.pasta.name)
        self.assertEqual(len(sistema.avisos), 1)
        self.assertEqual(sistema.clientes.total(), 0)