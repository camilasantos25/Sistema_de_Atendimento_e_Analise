import unittest
from estruturas.fila_prioridade import FilaPrioridade

class TestFilaPrioridade(unittest.TestCase):
    def setUp(self):
        self.fila = FilaPrioridade(2)

    def test_fila_nova_esta_vazia(self):
        self.assertTrue(self.fila.esta_vazia())
        self.assertEqual(self.fila.tamanho(), 0)

    def test_sair_de_fila_vazia_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.fila.sair()

    def test_espiar_fila_vazia_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.fila.espiar()

    def test_prioridade_maior_sai_primeiro(self):
        self.fila.entrar("Preferencial", 1)
        self.fila.entrar("Urgente", 2)
        self.assertEqual(self.fila.sair(), "Urgente")
        self.assertEqual(self.fila.sair(), "Preferencial")

    def test_mesma_prioridade_mantem_ordem_de_chegada(self):
        self.fila.entrar("P1", 1)
        self.fila.entrar("P2", 1)
        self.fila.entrar("P3", 1)
        self.assertEqual(self.fila.sair(), "P1")
        self.assertEqual(self.fila.sair(), "P2")
        self.assertEqual(self.fila.sair(), "P3")

    def test_urgente_chega_com_outros_aguardando(self):
        self.fila.entrar("P1", 1)
        self.fila.entrar("P2", 1)
        self.fila.entrar("U1", 2)
        self.fila.entrar("U2", 2)
        self.assertEqual(self.fila.sair(), "U1")

        self.fila.entrar("U3", 2)
        self.assertEqual(self.fila.sair(), "U2")
        self.assertEqual(self.fila.sair(), "U3")
        self.assertEqual(self.fila.sair(), "P1")
        self.assertEqual(self.fila.sair(), "P2")

    def test_prioridade_invalida_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.fila.entrar("X", 3)
        with self.assertRaises(ValueError):
            self.fila.entrar("X", -1)
        self.assertEqual(self.fila.tamanho(), 0)

    def test_espiar_nao_remove(self):
        self.fila.entrar("P1", 1)
        self.fila.entrar("U1", 2)
        self.assertEqual(self.fila.espiar(), "U1")
        self.assertEqual(self.fila.tamanho(), 2)

    def test_listar_na_ordem_de_chamada(self):
        self.fila.entrar("P1", 1)
        self.fila.entrar("U1", 2)
        self.fila.entrar("P2", 1)
        self.fila.entrar("U2", 2)
        self.assertEqual(self.fila.listar(), ["U1", "U2", "P1", "P2"])
        self.assertEqual(self.fila.tamanho(), 4)