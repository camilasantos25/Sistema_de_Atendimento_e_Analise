import unittest
from estruturas.ordenacao import insertion_sort, intercalar, merge_sort

class Item:
    def __init__(self, valor, ordem):
        self.valor = valor
        self.ordem = ordem

def pelo_valor(item):
    return item.valor

def ordens_do(itens):
    resultado = []
    for item in itens:
        resultado.append(item.ordem)
    return resultado

class TestInsertionSort(unittest.TestCase):
    def test_lista_vazia(self):
        self.assertEqual(insertion_sort([]), [])

    def test_um_elemento(self):
        self.assertEqual(insertion_sort([7]), [7])

    def test_lista_ja_ordenada(self):
        self.assertEqual(insertion_sort([1, 2, 3, 4]), [1, 2, 3, 4])

    def test_lista_em_ordem_inversa(self):
        self.assertEqual(insertion_sort([4, 3, 2, 1]), [1, 2, 3, 4])

    def test_com_valores_repetidos(self):
        self.assertEqual(insertion_sort([3, 1, 3, 2, 1]), [1, 1, 2, 3, 3])

    def test_nao_altera_a_lista_original(self):
        original = [3, 1, 2]
        resultado = insertion_sort(original)
        self.assertEqual(original, [3, 1, 2])
        self.assertEqual(resultado, [1, 2, 3])

    def test_confere_com_o_gabarito_do_python(self):
        lista = [9, 3, 7, 3, 1, 8, 2, 8, 0]
        self.assertEqual(insertion_sort(lista), sorted(lista))

    def test_ordena_objetos_pela_chave(self):
        itens = [Item(2, "a"), Item(1, "b"), Item(3, "c")]
        resultado = insertion_sort(itens, pelo_valor)
        self.assertEqual(ordens_do(resultado), ["b", "a", "c"])

    def test_e_estavel(self):
        itens = [Item(2, "a"), Item(1, "b"), Item(2, "c"), Item(1, "d")]
        resultado = insertion_sort(itens, pelo_valor)
        self.assertEqual(ordens_do(resultado), ["b", "d", "a", "c"])

class TestMergeSort(unittest.TestCase):
    def test_lista_vazia(self):
        self.assertEqual(merge_sort([]), [])

    def test_um_elemento(self):
        self.assertEqual(merge_sort([7]), [7])

    def test_lista_ja_ordenada(self):
        self.assertEqual(merge_sort([1, 2, 3, 4]), [1, 2, 3, 4])

    def test_lista_em_ordem_inversa(self):
        self.assertEqual(merge_sort([4, 3, 2, 1]), [1, 2, 3, 4])

    def test_com_valores_repetidos(self):
        self.assertEqual(merge_sort([3, 1, 3, 2, 1]), [1, 1, 2, 3, 3])

    def test_quantidade_impar_de_elementos(self):
        self.assertEqual(merge_sort([5, 2, 4, 1, 3]), [1, 2, 3, 4, 5])

    def test_nao_altera_a_lista_original(self):
        original = [3, 1, 2]
        resultado = merge_sort(original)
        self.assertEqual(original, [3, 1, 2])
        self.assertEqual(resultado, [1, 2, 3])

    def test_lista_maior_confere_com_o_gabarito(self):
        lista = list(range(50, 0, -1)) + list(range(1, 50, 3)) + [7, 7, 7]
        self.assertEqual(merge_sort(lista), sorted(lista))

    def test_ordena_objetos_pela_chave(self):
        itens = [Item(2, "a"), Item(1, "b"), Item(3, "c")]
        resultado = merge_sort(itens, pelo_valor)
        self.assertEqual(ordens_do(resultado), ["b", "a", "c"])

    def test_e_estavel(self):
        itens = [Item(2, "a"), Item(1, "b"), Item(2, "c"), Item(1, "d")]
        resultado = merge_sort(itens, pelo_valor)
        self.assertEqual(ordens_do(resultado), ["b", "d", "a", "c"])

class TestIntercalar(unittest.TestCase):
    def test_intercala_duas_listas(self):
        self.assertEqual(intercalar([1, 4, 6], [2, 3, 7]), [1, 2, 3, 4, 6, 7])

    def test_uma_das_listas_vazia(self):
        self.assertEqual(intercalar([], [1, 2]), [1, 2])
        self.assertEqual(intercalar([1, 2], []), [1, 2])

    def test_sobra_de_uma_lista_inteira(self):
        self.assertEqual(intercalar([1, 2], [3, 4]), [1, 2, 3, 4])
        self.assertEqual(intercalar([5, 6], [1, 2]), [1, 2, 5, 6])