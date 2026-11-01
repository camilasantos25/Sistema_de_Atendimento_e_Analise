import tempfile
import unittest
import os
from interface.menu import executar_menu
from interface.sistema import Sistema
from testes.apoio import entradas_falsas

def mensagens_do_log(capturado):
    resultado = []
    for registro in capturado.records:
        resultado.append(registro.getMessage())
    return resultado

class SistemaQueFalhaUmaVez:
    def __init__(self):
        self.tentativas = 0

    def salvar(self):
        self.tentativas = self.tentativas + 1
        if self.tentativas == 1:
            raise OSError("disco cheio")

class TestMenu(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.sistema = Sistema(self.pasta.name)
        self.saida = []

    def tearDown(self):
        self.pasta.cleanup()

    def rodar(self, respostas):
        executar_menu(self.sistema, entradas_falsas(respostas), self.saida.append)

    def test_menu_mostra_as_opcoes(self):
        self.rodar(["0"])
        self.assertIn("1 - Cadastrar cliente", self.saida)
        self.assertIn("0 - Salvar e sair", self.saida)

    def test_sair_salva_e_encerra(self):
        self.rodar(["0"])
        self.assertIn("Dados salvos. Até logo!", self.saida)
        self.assertTrue(os.path.exists(os.path.join(self.pasta.name, "clientes.csv")))

    def test_opcao_invalida(self):
        self.rodar(["99", "0"])
        self.assertIn("Opção inválida.", self.saida)

    def test_opcao_em_branco(self):
        self.rodar(["", "0"])
        self.assertIn("Opção inválida.", self.saida)

    def test_cadastrar_cliente_valido(self):
        self.rodar(["1", "1", "Ana", "11999990000", "0", "0"])
        self.assertEqual(self.sistema.clientes.total(), 1)
        self.assertEqual(self.sistema.clientes.buscar(1).nome, "Ana")
        self.assertIn("Cliente cadastrado!", self.saida)

    def test_cadastro_registra_no_log(self):
        with self.assertLogs("atendimento", level="INFO") as capturado:
            self.rodar(["1", "1", "Ana", "11999990000", "0", "0"])
        self.assertIn("Cliente 1 cadastrado", mensagens_do_log(capturado))

    def test_dados_invalidos_repetem_a_pergunta(self):
        self.rodar(["1", "0", "1", "Ana", "123", "11999990000", "7", "0", "0"])
        self.assertEqual(self.sistema.clientes.total(), 1)
        self.assertIn("Entrada inválida: O ID deve ser maior que zero.", self.saida)
        self.assertIn(
            "Entrada inválida: O telefone deve ter 10 ou 11 dígitos (com DDD).",
            self.saida,
        )
        self.assertIn("Entrada inválida: Prioridade inválida (use 0, 1 ou 2).", self.saida)

    def test_id_duplicado_e_recusado_e_registrado(self):
        self.sistema.clientes.cadastrar(1, "Ana", "11999990000", 0)

        with self.assertLogs("atendimento", level="WARNING") as capturado:
            self.rodar(["1", "1", "0"])

        self.assertEqual(self.sistema.clientes.total(), 1)
        self.assertIn(
            "Não foi possível concluir: Já existe um cliente com o ID 1.", self.saida
        )
        self.assertEqual(
            mensagens_do_log(capturado),
            ["Operação recusada: Já existe um cliente com o ID 1."],
        )

    def test_buscar_cliente_existente_e_inexistente(self):
        self.sistema.clientes.cadastrar(1, "Ana", "11999990000", 0)
        self.rodar(["2", "1", "2", "99", "0"])
        self.assertIn("ID 1 | Ana | 11999990000 | comum", self.saida)
        self.assertIn("Cliente não encontrado.", self.saida)

    def test_listar_sem_clientes(self):
        self.rodar(["3", "0"])
        self.assertIn("Nenhum cliente cadastrado.", self.saida)

    def test_listar_em_ordem_de_id(self):
        self.sistema.clientes.cadastrar(5, "Eva", "11999990002", 2)
        self.sistema.clientes.cadastrar(2, "Davi", "11999990001", 0)
        self.rodar(["3", "0"])

        linhas = []
        for texto in self.saida:
            if texto.startswith("ID "):
                linhas.append(texto)
        self.assertEqual(
            linhas,
            [
                "ID 2 | Davi | 11999990001 | comum",
                "ID 5 | Eva | 11999990002 | urgente",
            ],
        )

    def test_falha_ao_salvar_mantem_o_menu_aberto(self):
        falso = SistemaQueFalhaUmaVez()

        with self.assertLogs("atendimento", level="ERROR") as capturado:
            executar_menu(falso, entradas_falsas(["0", "0"]), self.saida.append)

        self.assertEqual(falso.tentativas, 2)
        self.assertIn("Não foi possível salvar os dados: disco cheio", self.saida)
        self.assertEqual(self.saida[-1], "Dados salvos. Até logo!")
        self.assertEqual(mensagens_do_log(capturado), ["Falha ao salvar: disco cheio"])