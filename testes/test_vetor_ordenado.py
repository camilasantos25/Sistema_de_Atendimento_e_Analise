import unittest
from estruturas.vetor_ordenado import VetorOrdenado

class ItemFalso:
    def __init__(self, id_item):
        self.id = id_item

def ids_do(vetor):
    ids = []
    for item in vetor.listar():
        ids.append(item.id)
    return ids

class TestVetorOrdenado(unittest.TestCase):
    def setUp(self):
        self.vetor = VetorOrdenado()

    def preencher(self):
        for id_item in [40, 8, 21, 3, 15]:
            self.vetor.inserir(ItemFalso(id_item))

    def test_buscar_em_vetor_vazio(self):
        self.assertIsNone(self.vetor.buscar(1))

    def test_inserir_mantem_ordem(self):
        self.preencher()
        self.assertEqual(ids_do(self.vetor), [3, 8, 15, 21, 40])

    def test_buscar_primeiro_e_ultimo(self):
        self.preencher()
        self.assertEqual(self.vetor.buscar(3).id, 3)
        self.assertEqual(self.vetor.buscar(40).id, 40)

    def test_buscar_inexistente(self):
        self.preencher()
        self.assertIsNone(self.vetor.buscar(99))

    def test_inserir_id_duplicado_levanta_erro(self):
        self.preencher()
        with self.assertRaises(ValueError):
            self.vetor.inserir(ItemFalso(8))
        self.assertEqual(self.vetor.tamanho(), 5)

    def test_remover_existente(self):
        self.preencher()
        removido = self.vetor.remover(15)
        self.assertEqual(removido.id, 15)
        self.assertEqual(ids_do(self.vetor), [3, 8, 21, 40])

    def test_remover_inexistente(self):
        self.preencher()
        self.assertIsNone(self.vetor.remover(99))
        self.assertEqual(self.vetor.tamanho(), 5)