import unittest
from datetime import datetime
from interface.apresentacao import (
    texto_da_duracao,
    texto_da_hora,
    texto_do_atendente,
    texto_do_atendimento,
)
from modelos.atendente import Atendente
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes

def hora(minuto):
    return datetime(2026, 10, 1, 10, minuto, 0)

class TestFormatos(unittest.TestCase):
    def test_duracao(self):
        self.assertEqual(texto_da_duracao(0), "0 s")
        self.assertEqual(texto_da_duracao(45), "45 s")
        self.assertEqual(texto_da_duracao(300.0), "5 min 0 s")
        self.assertEqual(texto_da_duracao(450.0), "7 min 30 s")
        self.assertEqual(texto_da_duracao(3725), "62 min 5 s")

    def test_duracao_arredonda(self):
        self.assertEqual(texto_da_duracao(59.6), "1 min 0 s")

    def test_hora(self):
        self.assertEqual(texto_da_hora(datetime(2026, 10, 1, 9, 5)), "01/10/2026 09:05")

    def test_atendente_livre_e_ocupado(self):
        atendente = Atendente(1, "Carla")
        self.assertEqual(texto_do_atendente(atendente), "ID 1 | Carla | livre")
        atendente.ocupado = True
        self.assertEqual(texto_do_atendente(atendente), "ID 1 | Carla | ocupado")

class TestTextoDoAtendimento(unittest.TestCase):
    def setUp(self):
        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.servico = ServicoAtendimentos(self.clientes, self.atendentes)
        self.clientes.cadastrar(1, "Ana", "11999990000", 0)
        self.atendentes.cadastrar(1, "Carla")

    def test_aguardando(self):
        atendimento = self.servico.abrir(1, hora(0))
        self.assertEqual(
            texto_do_atendimento(atendimento),
            "Atendimento 1 | Ana | aguardando | entrada 01/10/2026 10:00",
        )

    def test_em_andamento(self):
        self.servico.abrir(1, hora(0))
        atendimento = self.servico.chamar_proximo(1, hora(2))
        self.assertEqual(
            texto_do_atendimento(atendimento),
            "Atendimento 1 | Ana | em andamento | entrada 01/10/2026 10:00"
            " | atendente Carla",
        )

    def test_finalizado(self):
        self.servico.abrir(1, hora(0))
        self.servico.chamar_proximo(1, hora(2))
        atendimento = self.servico.finalizar(1, hora(7))
        self.assertEqual(
            texto_do_atendimento(atendimento),
            "Atendimento 1 | Ana | finalizado | entrada 01/10/2026 10:00"
            " | atendente Carla | duração 5 min 0 s",
        )