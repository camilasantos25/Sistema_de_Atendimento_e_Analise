import unittest
from datetime import datetime
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes

def hora(minuto, segundo=0):
    return datetime(2026, 10, 17, 10, minuto, segundo)

class TestDesfazerFinalizacao(unittest.TestCase):
    def setUp(self):
        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.servico = ServicoAtendimentos(self.clientes, self.atendentes)

        self.clientes.cadastrar(1, "Ana", "11999990000", 0)
        self.clientes.cadastrar(2, "Davi", "11999990001", 0)
        self.atendentes.cadastrar(1, "Carla")
        self.atendentes.cadastrar(2, "Paulo")

    def test_desfazer_sem_nada_para_desfazer(self):
        with self.assertRaises(ValueError):
            self.servico.desfazer_finalizacao()

    def test_desfazer_restaura_o_estado_anterior(self):
        self.servico.abrir(1, hora(0))
        self.servico.chamar_proximo(1, hora(2))
        self.servico.finalizar(1, hora(7))

        atendimento = self.servico.desfazer_finalizacao()

        self.assertEqual(atendimento.estado, "em_andamento")
        self.assertIsNone(atendimento.hora_fim)
        self.assertTrue(self.atendentes.buscar(1).ocupado)
        self.assertEqual(len(self.servico.historico_do_cliente(1)), 0)
        self.assertTrue(self.servico.pilha_desfazer.esta_vazia())

        refeito = self.servico.finalizar(1, hora(9))
        self.assertEqual(refeito.duracao_segundos(), 420.0)

    def test_desfazer_recusado_se_atendente_ocupado(self):
        self.servico.abrir(1)
        self.servico.abrir(2)
        self.servico.chamar_proximo(1)
        self.servico.finalizar(1)
        self.servico.chamar_proximo(1)

        with self.assertRaises(ValueError):
            self.servico.desfazer_finalizacao()

        self.assertEqual(len(self.servico.historico), 1)
        self.assertEqual(self.servico.pilha_desfazer.tamanho(), 1)
        self.assertTrue(self.atendentes.buscar(1).ocupado)

    def test_desfazer_recusado_se_cliente_abriu_outro_atendimento(self):
        self.servico.abrir(1)
        self.servico.chamar_proximo(1)
        self.servico.finalizar(1)
        self.servico.abrir(1)

        with self.assertRaises(ValueError):
            self.servico.desfazer_finalizacao()

        self.assertEqual(len(self.servico.historico), 1)
        self.assertEqual(self.servico.pilha_desfazer.tamanho(), 1)

    def test_desfazer_segue_a_ordem_lifo(self):
        self.servico.abrir(1)
        self.servico.abrir(2)
        self.servico.chamar_proximo(1)
        self.servico.chamar_proximo(2)
        self.servico.finalizar(1)
        self.servico.finalizar(2)

        primeiro = self.servico.desfazer_finalizacao()
        self.assertEqual(primeiro.cliente.id, 2)

        segundo = self.servico.desfazer_finalizacao()
        self.assertEqual(segundo.cliente.id, 1)

        self.assertEqual(len(self.servico.historico), 0)