import unittest
from datetime import datetime
from estruturas.lista_encadeada import ListaEncadeada
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes

class ItemFalso:
    def __init__(self, id_item):
        self.id = id_item

def ids(itens):
    resultado = []
    for item in itens:
        resultado.append(item.id)
    return resultado

def dia(numero):
    return datetime(2026, 10, numero, 10, 0, 0)

def maior_que_dez(item):
    return item.id > 10

def dois_ou_tres(item):
    return item.id == 2 or item.id == 3

def menor_que_tres(item):
    return item.id < 3

def maior_que_tres(item):
    return item.id > 3

def todos(item):
    return True

class TestRemoverSeDaLista(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()

    def preencher(self):
        for id_item in [1, 2, 3, 4, 5]:
            self.lista.inserir_no_fim(ItemFalso(id_item))

    def test_remover_se_em_lista_vazia(self):
        self.assertEqual(self.lista.remover_se(todos), [])
        self.assertTrue(self.lista.esta_vazia())

    def test_nenhum_item_satisfaz(self):
        self.preencher()
        self.assertEqual(self.lista.remover_se(maior_que_dez), [])
        self.assertEqual(ids(self.lista.listar()), [1, 2, 3, 4, 5])
        self.assertEqual(self.lista.tamanho(), 5)

    def test_remove_itens_consecutivos_do_meio(self):
        self.preencher()
        removidos = self.lista.remover_se(dois_ou_tres)
        self.assertEqual(ids(removidos), [2, 3])
        self.assertEqual(ids(self.lista.listar()), [1, 4, 5])
        self.assertEqual(self.lista.tamanho(), 3)

    def test_remove_a_cabeca_e_o_seguinte(self):
        self.preencher()
        self.lista.remover_se(menor_que_tres)
        self.assertEqual(ids(self.lista.listar()), [3, 4, 5])

    def test_remove_a_cauda_e_continua_aceitando_inserir_no_fim(self):
        self.preencher()
        self.lista.remover_se(maior_que_tres)
        self.assertEqual(ids(self.lista.listar()), [1, 2, 3])

        self.lista.inserir_no_fim(ItemFalso(6))
        self.assertEqual(ids(self.lista.listar()), [1, 2, 3, 6])

    def test_remove_todos_e_lista_continua_utilizavel(self):
        self.preencher()
        self.lista.remover_se(todos)
        self.assertTrue(self.lista.esta_vazia())
        self.assertEqual(self.lista.tamanho(), 0)

        self.lista.inserir_no_fim(ItemFalso(9))
        self.assertEqual(ids(self.lista.listar()), [9])

class TestClientesInativos(unittest.TestCase):
    def setUp(self):
        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.servico = ServicoAtendimentos(self.clientes, self.atendentes)

        self.clientes.cadastrar(1, "Ana", "11999990000", 0, dia(1))
        self.clientes.cadastrar(2, "Davi", "11999990001", 0, dia(10))
        self.clientes.cadastrar(3, "Eva", "11999990002", 0, dia(20))
        self.atendentes.cadastrar(1, "Carla")

    def test_remover_cliente_inexistente(self):
        with self.assertRaises(ValueError):
            self.servico.remover_cliente(99)

    def test_remover_cliente_com_atendimento_aberto_recusado(self):
        self.servico.abrir(1, dia(25))
        with self.assertRaises(ValueError):
            self.servico.remover_cliente(1)

        self.servico.chamar_proximo(1, dia(25))
        with self.assertRaises(ValueError):
            self.servico.remover_cliente(1)

        self.assertIsNotNone(self.clientes.buscar(1))
        self.assertEqual(self.clientes.total(), 3)
        self.assertEqual(self.clientes.total_ativos(), 3)

    def test_remover_cliente_valido_sai_das_duas_estruturas(self):
        removido = self.servico.remover_cliente(2)
        self.assertEqual(removido.id, 2)
        self.assertIsNone(self.clientes.buscar(2))
        self.assertEqual(self.clientes.total(), 2)
        self.assertEqual(self.clientes.total_ativos(), 2)

    def test_remover_inativos(self):
        removidos = self.servico.remover_clientes_inativos(10, dia(28))
        self.assertEqual(ids(removidos), [1, 2])
        self.assertIsNone(self.clientes.buscar(1))
        self.assertIsNotNone(self.clientes.buscar(3))
        self.assertEqual(self.clientes.total(), 1)
        self.assertEqual(self.clientes.total_ativos(), 1)

    def test_inativo_com_atendimento_aberto_nao_e_removido(self):
        self.servico.abrir(1, dia(25))
        removidos = self.servico.remover_clientes_inativos(10, dia(28))
        self.assertEqual(ids(removidos), [2])
        self.assertIsNotNone(self.clientes.buscar(1))
        self.assertEqual(self.clientes.total(), 2)

    def test_finalizacao_conta_como_atividade(self):
        self.servico.abrir(1, dia(2))
        self.servico.chamar_proximo(1, dia(2))
        self.servico.finalizar(1, dia(26))

        removidos = self.servico.remover_clientes_inativos(10, dia(28))
        self.assertEqual(ids(removidos), [2])
        self.assertIsNotNone(self.clientes.buscar(1))
        self.assertIsNotNone(self.clientes.buscar(3))

    def test_dias_negativos_recusado(self):
        with self.assertRaises(ValueError):
            self.servico.remover_clientes_inativos(-1, dia(28))

    def test_nenhum_cliente_inativo(self):
        removidos = self.servico.remover_clientes_inativos(30, dia(21))
        self.assertEqual(removidos, [])
        self.assertEqual(self.clientes.total(), 3)

    def test_desfazer_devolve_a_ultima_atividade_anterior(self):
        self.servico.abrir(1, dia(2))
        self.servico.chamar_proximo(1, dia(2))
        self.servico.finalizar(1, dia(26))
        self.assertEqual(self.clientes.buscar(1).ultima_atividade, dia(26))

        self.servico.desfazer_finalizacao()
        self.assertEqual(self.clientes.buscar(1).ultima_atividade, dia(1))

    def test_desfazer_recusado_se_cliente_foi_removido(self):
        self.servico.abrir(1, dia(2))
        self.servico.chamar_proximo(1, dia(2))
        self.servico.finalizar(1, dia(26))
        self.servico.remover_cliente(1)

        with self.assertRaises(ValueError):
            self.servico.desfazer_finalizacao()

        self.assertEqual(len(self.servico.historico_do_cliente(1)), 1)
        self.assertEqual(self.servico.pilha_desfazer.tamanho(), 1)
        self.assertFalse(self.atendentes.buscar(1).ocupado)

    def test_desfazer_recusado_se_o_id_foi_reutilizado(self):
        self.servico.abrir(1, dia(2))
        self.servico.chamar_proximo(1, dia(2))
        self.servico.finalizar(1, dia(26))
        self.servico.remover_cliente(1)
        self.clientes.cadastrar(1, "Outra Ana", "11999990009", 0, dia(27))

        with self.assertRaises(ValueError):
            self.servico.desfazer_finalizacao()

        self.assertEqual(self.servico.pilha_desfazer.tamanho(), 1)