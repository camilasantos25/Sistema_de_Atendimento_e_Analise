import unittest
from datetime import date
from interface.entrada import converter_data, ler_valor, validar_nao_negativo
from testes.apoio import entradas_falsas

class TestConversoresNovos(unittest.TestCase):
    def test_data_valida_com_espacos(self):
        self.assertEqual(converter_data("01/10/2026"), date(2026, 10, 1))
        self.assertEqual(converter_data(" 25/10/2026 "), date(2026, 10, 25))

    def test_data_sem_zero_a_esquerda(self):
        self.assertEqual(converter_data("1/10/2026"), date(2026, 10, 1))

    def test_data_invalida(self):
        for texto in ["31/02/2026", "2026-10-01", "abc", ""]:
            with self.assertRaises(ValueError):
                converter_data(texto)

    def test_nao_negativo(self):
        self.assertIsNone(validar_nao_negativo(0))
        with self.assertRaises(ValueError):
            validar_nao_negativo(-1)

    def test_ler_data_repete_ate_acertar(self):
        mensagens = []
        valor = ler_valor(
            "Data: ", converter_data,
            entrada=entradas_falsas(["abc", "01/10/2026"]), saida=mensagens.append,
        )
        self.assertEqual(valor, date(2026, 10, 1))
        self.assertEqual(
            mensagens,
            ["Entrada inválida: Digite a data no formato DD/MM/AAAA, por exemplo 25/10/2026."],
        )