import unittest
from estruturas.pilha import Pilha

class TestPilha(unittest.TestCase):
    def setUp(self):
        self.pilha = Pilha()

    def test_pilha_nova_esta_vazia(self):
        self.assertTrue(self.pilha.esta_vazia())
        self.assertEqual(self.pilha.tamanho(), 0)

    def test_desempilhar_pilha_vazia_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.pilha.desempilhar()

    def test_topo_de_pilha_vazia_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.pilha.topo()

    def test_ultimo_a_entrar_e_o_primeiro_a_sair(self):
        self.pilha.empilhar("A")
        self.pilha.empilhar("B")
        self.pilha.empilhar("C")
        self.assertEqual(self.pilha.desempilhar(), "C")
        self.assertEqual(self.pilha.desempilhar(), "B")
        self.assertEqual(self.pilha.desempilhar(), "A")
        self.assertTrue(self.pilha.esta_vazia())

    def test_topo_nao_remove(self):
        self.pilha.empilhar("A")
        self.pilha.empilhar("B")
        self.assertEqual(self.pilha.topo(), "B")
        self.assertEqual(self.pilha.tamanho(), 2)

    def test_listar_da_base_ao_topo_sem_alterar(self):
        self.pilha.empilhar("A")
        self.pilha.empilhar("B")
        self.assertEqual(self.pilha.listar(), ["A", "B"])
        self.assertEqual(self.pilha.tamanho(), 2)