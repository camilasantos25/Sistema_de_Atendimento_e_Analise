import unittest
from datetime import date, datetime
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes
from servicos.servico_relatorios import ServicoRelatorios

def hora(dia, horas, minutos):
    return datetime(2026, 10, dia, horas, minutos, 0)

def resumo(pares):
    resultado = []
    for par in pares:
        resultado.append((par[0].id, par[1]))
    return resultado

def ids(atendimentos):
    resultado = []
    for atendimento in atendimentos:
        resultado.append(atendimento.cliente.id)
    return resultado

class TestServicoRelatorios(unittest.TestCase):
    def setUp(self):
        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.atendimentos = ServicoAtendimentos(self.clientes, self.atendentes)
        self.relatorios = ServicoRelatorios(self.atendimentos)

        self.clientes.cadastrar(1, "Ana", "11999990000", 0)
        self.clientes.cadastrar(2, "Davi", "11999990001", 0)
        self.clientes.cadastrar(3, "Eva", "11999990002", 2)
        self.atendentes.cadastrar(1, "Carla")
        self.atendentes.cadastrar(2, "Paulo")

    def atender(self, id_cliente, dia, minuto_inicio, minuto_fim):
        self.atendimentos.abrir(id_cliente, hora(dia, 10, minuto_inicio))
        self.atendimentos.chamar_proximo(1, hora(dia, 10, minuto_inicio))
        self.atendimentos.finalizar(1, hora(dia, 10, minuto_fim))

    def test_tempo_medio_sem_historico(self):
        self.assertIsNone(self.relatorios.tempo_medio_segundos())

    def test_tempo_medio_com_dois_atendimentos(self):
        self.atender(1, 1, 0, 5)
        self.atender(2, 1, 10, 20)
        self.assertEqual(self.relatorios.tempo_medio_segundos(), 450.0)

    def test_top_clientes_sem_historico(self):
        self.assertEqual(self.relatorios.top_clientes(), [])

    def test_top_clientes_ordena_por_total_e_desempata_por_id(self):
        self.atender(3, 1, 0, 5)
        self.atender(2, 1, 10, 15)
        self.atender(1, 1, 20, 25)
        self.atender(2, 1, 30, 35)

        top = self.relatorios.top_clientes()
        self.assertEqual(resumo(top), [(2, 2), (1, 1), (3, 1)])

    def test_top_clientes_respeita_a_quantidade(self):
        self.atender(3, 1, 0, 5)
        self.atender(2, 1, 10, 15)
        self.atender(1, 1, 20, 25)
        self.atender(2, 1, 30, 35)

        top = self.relatorios.top_clientes(2)
        self.assertEqual(resumo(top), [(2, 2), (1, 1)])

    def test_top_clientes_quantidade_invalida(self):
        with self.assertRaises(ValueError):
            self.relatorios.top_clientes(0)
        with self.assertRaises(ValueError):
            self.relatorios.top_clientes(-1)

    def test_filtrar_um_dia_e_um_intervalo(self):
        self.atender(1, 1, 0, 5)
        self.atender(2, 2, 0, 5)
        self.atender(3, 3, 0, 5)

        so_dia_2 = self.relatorios.filtrar_por_data(date(2026, 10, 2), date(2026, 10, 2))
        self.assertEqual(ids(so_dia_2), [2])

        dias_1_a_2 = self.relatorios.filtrar_por_data(date(2026, 10, 1), date(2026, 10, 2))
        self.assertEqual(ids(dias_1_a_2), [1, 2])

    def test_filtrar_sem_resultados(self):
        self.atender(1, 1, 0, 5)
        encontrados = self.relatorios.filtrar_por_data(date(2026, 10, 10), date(2026, 10, 20))
        self.assertEqual(encontrados, [])

    def test_filtrar_ordena_pela_hora_de_inicio(self):
        self.atendimentos.abrir(1, hora(1, 9, 50))
        self.atendimentos.abrir(2, hora(1, 9, 55))
        self.atendimentos.chamar_proximo(1, hora(1, 10, 0))
        self.atendimentos.chamar_proximo(2, hora(1, 10, 10))
        self.atendimentos.finalizar(2, hora(1, 10, 20))
        self.atendimentos.finalizar(1, hora(1, 10, 30))

        self.assertEqual(ids(self.atendimentos.historico), [2, 1])

        encontrados = self.relatorios.filtrar_por_data(date(2026, 10, 1), date(2026, 10, 1))
        self.assertEqual(ids(encontrados), [1, 2])

    def test_filtrar_data_inicial_depois_da_final(self):
        with self.assertRaises(ValueError):
            self.relatorios.filtrar_por_data(date(2026, 10, 5), date(2026, 10, 1))

    def test_alertas_sem_ninguem_esperando(self):
        self.assertEqual(self.relatorios.alertas_de_espera(900, hora(1, 10, 30)), [])

    def test_alertas_mostram_quem_espera_mais_primeiro(self):
        self.atendimentos.abrir(1, hora(1, 10, 0))
        self.atendimentos.abrir(3, hora(1, 10, 5))
        self.atendimentos.abrir(2, hora(1, 10, 20))

        alertas = self.relatorios.alertas_de_espera(900, hora(1, 10, 30))

        resultado = []
        for atendimento, espera in alertas:
            resultado.append((atendimento.cliente.id, espera))
        self.assertEqual(resultado, [(1, 1800.0), (3, 1500.0)])

        self.assertEqual(self.atendimentos.fila_comum.tamanho(), 2)
        self.assertEqual(self.atendimentos.fila_prioridade.tamanho(), 1)

    def test_alertas_ignoram_quem_ja_esta_em_atendimento(self):
        self.atendimentos.abrir(1, hora(1, 10, 0))
        self.atendimentos.chamar_proximo(1, hora(1, 10, 5))
        self.assertEqual(self.relatorios.alertas_de_espera(0, hora(1, 11, 0)), [])

    def test_alerta_so_quando_a_espera_passa_do_limite(self):
        self.atendimentos.abrir(1, hora(1, 10, 0))
        self.assertEqual(self.relatorios.alertas_de_espera(900, hora(1, 10, 15)), [])

    def test_alertas_limite_negativo(self):
        with self.assertRaises(ValueError):
            self.relatorios.alertas_de_espera(-1, hora(1, 10, 0))