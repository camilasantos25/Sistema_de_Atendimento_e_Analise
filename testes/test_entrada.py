import unittest
from interface.entrada import converter_inteiro, converter_texto, ler_valor
from modelos.cliente import validar_prioridade, validar_telefone
from modelos.validacoes import validar_id, validar_nome
from testes.apoio import entradas_falsas

class TestConversores(unittest.TestCase):
    def test_inteiro_aceita_espacos(self):
        self.assertEqual(converter_inteiro(" 42 "), 42)

    def test_inteiro_invalido(self):
        for texto in ["abc", "", "3.5"]:
            with self.assertRaises(ValueError):
                converter_inteiro(texto)

    def test_inteiro_mensagem_em_portugues(self):
        with self.assertRaises(ValueError) as contexto:
            converter_inteiro("abc")
        self.assertEqual(str(contexto.exception), "Digite um número inteiro.")

    def test_texto_tira_espacos(self):
        self.assertEqual(converter_texto("  Ana  "), "Ana")

class TestLerValor(unittest.TestCase):
    def setUp(self):
        self.mensagens = []

    def test_valor_valido_na_primeira_tentativa(self):
        valor = ler_valor(
            "ID: ", converter_inteiro, validar_id,
            entradas_falsas(["7"]), self.mensagens.append,
        )
        self.assertEqual(valor, 7)
        self.assertEqual(self.mensagens, [])

    def test_repete_ate_acertar(self):
        valor = ler_valor(
            "ID: ", converter_inteiro, validar_id,
            entradas_falsas(["abc", "-3", "7"]), self.mensagens.append,
        )
        self.assertEqual(valor, 7)
        self.assertEqual(
            self.mensagens,
            [
                "Entrada inválida: Digite um número inteiro.",
                "Entrada inválida: O ID deve ser maior que zero.",
            ],
        )

    def test_sem_validador(self):
        valor = ler_valor(
            "Dias: ", converter_inteiro,
            entrada=entradas_falsas(["abc", "10"]), saida=self.mensagens.append,
        )
        self.assertEqual(valor, 10)
        self.assertEqual(len(self.mensagens), 1)

    def test_nome_vazio_e_recusado(self):
        valor = ler_valor(
            "Nome: ", converter_texto, validar_nome,
            entradas_falsas(["   ", "Ana"]), self.mensagens.append,
        )
        self.assertEqual(valor, "Ana")
        self.assertEqual(self.mensagens, ["Entrada inválida: O nome não pode ficar vazio."])

    def test_telefone_com_letras_ou_curto_e_recusado(self):
        valor = ler_valor(
            "Telefone: ", converter_texto, validar_telefone,
            entradas_falsas(["abc", "123", "11999990000"]), self.mensagens.append,
        )
        self.assertEqual(valor, "11999990000")
        self.assertEqual(len(self.mensagens), 2)

    def test_prioridade_fora_da_lista_e_recusada(self):
        valor = ler_valor(
            "Prioridade: ", converter_inteiro, validar_prioridade,
            entradas_falsas(["5", "2"]), self.mensagens.append,
        )
        self.assertEqual(valor, 2)
        self.assertEqual(
            self.mensagens,
            ["Entrada inválida: Prioridade inválida (use 0, 1 ou 2)."],
        )