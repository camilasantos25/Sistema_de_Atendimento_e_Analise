import unittest
from estruturas.lista_encadeada import ListaEncadeada

class ItemFalso:
    def __init__(self, id_item):
        self.id = id_item

def ids_do(lista):
    ids = []
    for item in lista.listar():
        ids.append(item.id)
    return ids

class TestListaEncadeada(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()

    def preencher(self):
        for id_item in [1, 2, 3]:
            self.lista.inserir_no_fim(ItemFalso(id_item))

    def test_lista_nova_esta_vazia(self):
        self.assertTrue(self.lista.esta_vazia())
        self.assertEqual(self.lista.tamanho(), 0)
        self.assertEqual(self.lista.listar(), [])

    def test_buscar_e_remover_em_lista_vazia(self):
        self.assertIsNone(self.lista.buscar(1))
        self.assertIsNone(self.lista.remover(1))

    def test_inserir_no_fim_mantem_ordem_de_chegada(self):
        self.preencher()
        self.assertEqual(ids_do(self.lista), [1, 2, 3])
        self.assertEqual(self.lista.tamanho(), 3)

    def test_inserir_no_inicio_inverte_a_ordem(self):
        for id_item in [1, 2, 3]:
            self.lista.inserir_no_inicio(ItemFalso(id_item))
        self.assertEqual(ids_do(self.lista), [3, 2, 1])

    def test_buscar_existente_e_inexistente(self):
        self.preencher()
        self.assertEqual(self.lista.buscar(2).id, 2)
        self.assertIsNone(self.lista.buscar(99))

    def test_remover_a_cabeca(self):
        self.preencher()
        removido = self.lista.remover(1)
        self.assertEqual(removido.id, 1)
        self.assertEqual(ids_do(self.lista), [2, 3])
        self.assertEqual(self.lista.tamanho(), 2)

    def test_remover_do_meio(self):
        self.preencher()
        removido = self.lista.remover(2)
        self.assertEqual(removido.id, 2)
        self.assertEqual(ids_do(self.lista), [1, 3])

    def test_remover_a_cauda_e_inserir_no_fim(self):
        self.preencher()
        removido = self.lista.remover(3)
        self.assertEqual(removido.id, 3)
        self.assertEqual(ids_do(self.lista), [1, 2])

        self.lista.inserir_no_fim(ItemFalso(4))
        self.assertEqual(ids_do(self.lista), [1, 2, 4])
        self.assertEqual(self.lista.tamanho(), 3)

    def test_remover_o_unico_elemento(self):
        self.lista.inserir_no_fim(ItemFalso(7))
        self.lista.remover(7)
        self.assertTrue(self.lista.esta_vazia())
        self.assertEqual(self.lista.tamanho(), 0)

        self.lista.inserir_no_fim(ItemFalso(8))
        self.assertEqual(ids_do(self.lista), [8])

    def test_remover_inexistente_nao_altera(self):
        self.preencher()
        self.assertIsNone(self.lista.remover(99))
        self.assertEqual(ids_do(self.lista), [1, 2, 3])
        self.assertEqual(self.lista.tamanho(), 3)