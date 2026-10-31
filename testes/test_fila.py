import unittest
from estruturas.fila import Fila

class TestFila(unittest.TestCase):
    def setUp(self):
        self.fila = Fila()

    def test_fila_nova_esta_vazia(self):
        self.assertTrue(self.fila.esta_vazia())
        self.assertEqual(self.fila.tamanho(), 0)

    def test_sair_de_fila_vazia_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.fila.sair()

    def test_espiar_fila_vazia_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.fila.espiar()

    def test_primeiro_a_entrar_e_o_primeiro_a_sair(self):
        self.fila.entrar("Ana")
        self.fila.entrar("Davi")
        self.fila.entrar("Beatriz")
        self.assertEqual(self.fila.sair(), "Ana")
        self.assertEqual(self.fila.sair(), "Davi")
        self.assertEqual(self.fila.sair(), "Beatriz")
        self.assertTrue(self.fila.esta_vazia())

    def test_espiar_nao_remove(self):
        self.fila.entrar("Ana")
        self.fila.entrar("Davi")
        self.assertEqual(self.fila.espiar(), "Ana")
        self.assertEqual(self.fila.tamanho(), 2)

    def test_entrar_depois_de_sair(self):
        self.fila.entrar("Ana")
        self.fila.entrar("Davi")
        self.fila.sair()
        self.fila.entrar("Eva")
        self.assertEqual(self.fila.listar(), ["Davi", "Eva"])

    def test_limpeza_mantem_a_ordem(self):
        for numero in range(100):
            self.fila.entrar(numero)
        for numero in range(60):
            self.assertEqual(self.fila.sair(), numero)

        self.assertEqual(self.fila.tamanho(), 40)
        self.assertEqual(self.fila.listar(), list(range(60, 100)))

        self.fila.entrar(100)
        self.assertEqual(self.fila.sair(), 60)
        self.assertEqual(self.fila.listar()[-1], 100)