import unittest
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_clientes import ServicoClientes

class TestServicoClientes(unittest.TestCase):
    def setUp(self):
        self.servico = ServicoClientes()

    def test_cadastro_valido(self):
        cliente = self.servico.cadastrar(8, "Ana", "11999990000", 2)
        self.assertEqual(cliente.id, 8)
        self.assertEqual(self.servico.total(), 1)
        self.assertIsNotNone(self.servico.buscar(8))

    def test_id_duplicado_recusado(self):
        self.servico.cadastrar(8, "Ana", "11999990000", 2)
        with self.assertRaises(ValueError):
            self.servico.cadastrar(8, "Outra Ana", "11900001111", 0)
        self.assertEqual(self.servico.total(), 1)

    def test_dados_invalidos_nao_deixam_residuo(self):
        with self.assertRaises(ValueError):
            self.servico.cadastrar(5, "Eva", "abc", 0)
        self.assertEqual(self.servico.total(), 0)

    def test_buscar_inexistente(self):
        self.assertIsNone(self.servico.buscar(99))


class TestServicoAtendentes(unittest.TestCase):
    def setUp(self):
        self.servico = ServicoAtendentes()

    def test_cadastro_valido(self):
        atendente = self.servico.cadastrar(1, "Carla")
        self.assertEqual(atendente.nome, "Carla")
        self.assertEqual(self.servico.total(), 1)

    def test_id_duplicado_recusado(self):
        self.servico.cadastrar(1, "Carla")
        with self.assertRaises(ValueError):
            self.servico.cadastrar(1, "Outra Carla")
        self.assertEqual(self.servico.total(), 1)

    def test_nome_vazio_recusado(self):
        with self.assertRaises(ValueError):
            self.servico.cadastrar(2, "   ")
        self.assertEqual(self.servico.total(), 0)