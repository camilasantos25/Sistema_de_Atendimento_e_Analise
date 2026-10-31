import unittest
from datetime import datetime
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes

def hora(minuto, segundo=0):
    return datetime(2026, 10, 17, 10, minuto, segundo)

class TestServicoAtendimentos(unittest.TestCase):
    def setUp(self):
        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.servico = ServicoAtendimentos(self.clientes, self.atendentes)

        self.clientes.cadastrar(1, "Ana", "11999990000", 0)
        self.clientes.cadastrar(2, "Davi", "11999990001", 0)
        self.clientes.cadastrar(3, "Beatriz", "11999990002", 1)
        self.clientes.cadastrar(4, "Eva", "11999990003", 2)
        self.atendentes.cadastrar(1, "Carla")
        self.atendentes.cadastrar(2, "Paulo")

    def test_abrir_cliente_inexistente(self):
        with self.assertRaises(ValueError):
            self.servico.abrir(99)

    def test_abrir_duas_vezes_recusado(self):
        self.servico.abrir(1)
        with self.assertRaises(ValueError):
            self.servico.abrir(1)

    def test_chamar_com_filas_vazias(self):
        with self.assertRaises(ValueError):
            self.servico.chamar_proximo(1)

    def test_chamar_com_atendente_inexistente(self):
        self.servico.abrir(1)
        with self.assertRaises(ValueError):
            self.servico.chamar_proximo(99)

    def test_prioridade_antes_do_comum(self):
        self.servico.abrir(1)
        self.servico.abrir(3)
        self.servico.abrir(4)
        self.assertEqual(self.servico.chamar_proximo(1).cliente.id, 4)
        self.assertEqual(self.servico.chamar_proximo(2).cliente.id, 3)

    def test_mesma_prioridade_ordem_de_chegada(self):
        self.servico.abrir(1)
        self.servico.abrir(2)
        self.assertEqual(self.servico.chamar_proximo(1).cliente.id, 1)
        self.servico.finalizar(1)
        self.assertEqual(self.servico.chamar_proximo(1).cliente.id, 2)

    def test_atendente_ocupado_recusado(self):
        self.servico.abrir(1)
        self.servico.abrir(2)
        self.servico.chamar_proximo(1)
        with self.assertRaises(ValueError):
            self.servico.chamar_proximo(1)
        self.assertEqual(self.servico.fila_comum.tamanho(), 1)

    def test_finalizar_sem_atendimento_em_andamento(self):
        with self.assertRaises(ValueError):
            self.servico.finalizar(1)

    def test_finalizacao_valida(self):
        self.servico.abrir(1, hora(0))
        self.servico.chamar_proximo(1, hora(2))
        atendimento = self.servico.finalizar(1, hora(7, 30))

        self.assertEqual(atendimento.duracao_segundos(), 330.0)
        self.assertEqual(atendimento.espera_segundos(), 120.0)
        self.assertEqual(atendimento.atendente.id, 1)
        self.assertFalse(self.atendentes.buscar(1).ocupado)
        self.assertEqual(len(self.servico.historico_do_cliente(1)), 1)

    def test_cliente_pode_voltar_depois_de_finalizar(self):
        self.servico.abrir(1)
        self.servico.chamar_proximo(1)
        self.servico.finalizar(1)
        self.servico.abrir(1)
        self.assertEqual(self.servico.fila_comum.tamanho(), 1)