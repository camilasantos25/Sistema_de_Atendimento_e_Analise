import os
import tempfile
import unittest
from datetime import datetime
from persistencia.armazenamento import carregar_sistema, salvar_sistema
from persistencia.exportacao import gravar_csv
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes

def hora(dia, horas, minutos):
    return datetime(2026, 10, dia, horas, minutos, 0)

def ids(itens):
    resultado = []
    for item in itens:
        resultado.append(item.id)
    return resultado

class TestSalvarECarregar(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.clientes = ServicoClientes()
        self.atendentes = ServicoAtendentes()
        self.atendimentos = ServicoAtendimentos(self.clientes, self.atendentes)
        self.montar_cenario()

    def tearDown(self):
        self.pasta.cleanup()

    def montar_cenario(self):
        self.clientes.cadastrar(1, "Ana", "11999990000", 0, hora(1, 9, 0))
        self.clientes.cadastrar(2, "Davi", "11999990001", 0, hora(1, 9, 0))
        self.clientes.cadastrar(3, "Eva", "11999990002", 2, hora(1, 9, 0))
        self.clientes.cadastrar(4, "Beto", "11999990003", 1, hora(1, 9, 0))
        self.clientes.cadastrar(5, "Lia", "11999990004", 0, hora(1, 9, 0))
        self.atendentes.cadastrar(1, "Carla")
        self.atendentes.cadastrar(2, "Paulo")

        self.atendimentos.abrir(1, hora(1, 10, 0))
        self.atendimentos.chamar_proximo(1, hora(1, 10, 0))
        self.atendimentos.finalizar(1, hora(1, 10, 5))
        self.atendimentos.abrir(2, hora(1, 10, 10))
        self.atendimentos.chamar_proximo(1, hora(1, 10, 10))
        self.atendimentos.finalizar(1, hora(1, 10, 20))

        self.atendimentos.abrir(1, hora(1, 10, 30))
        self.atendimentos.abrir(3, hora(1, 10, 32))
        self.atendimentos.abrir(4, hora(1, 10, 33))
        self.atendimentos.abrir(5, hora(1, 10, 34))
        self.atendimentos.chamar_proximo(2, hora(1, 10, 40))

    def ida_e_volta(self):
        salvar_sistema(self.pasta.name, self.clientes, self.atendentes, self.atendimentos)
        return carregar_sistema(self.pasta.name)

    def test_salvar_cria_os_tres_arquivos(self):
        salvar_sistema(self.pasta.name, self.clientes, self.atendentes, self.atendimentos)
        for nome in ["clientes.csv", "atendentes.csv", "atendimentos.csv"]:
            self.assertTrue(os.path.exists(os.path.join(self.pasta.name, nome)))

    def test_clientes_e_atendentes_voltam_iguais(self):
        clientes, atendentes, atendimentos, avisos = self.ida_e_volta()

        self.assertEqual(avisos, [])
        self.assertEqual(ids(clientes.listar()), [1, 2, 3, 4, 5])
        self.assertEqual(clientes.total_ativos(), 5)

        eva = clientes.buscar(3)
        self.assertEqual(eva.nome, "Eva")
        self.assertEqual(eva.telefone, "11999990002")
        self.assertEqual(eva.prioridade, 2)

        self.assertEqual(clientes.buscar(1).ultima_atividade, hora(1, 10, 5))
        self.assertEqual(clientes.buscar(5).ultima_atividade, hora(1, 9, 0))

        self.assertEqual(ids(atendentes.listar()), [1, 2])
        self.assertTrue(atendentes.buscar(2).ocupado)
        self.assertFalse(atendentes.buscar(1).ocupado)

    def test_atendimento_em_andamento_volta_ligado_aos_mesmos_objetos(self):
        clientes, atendentes, atendimentos, avisos = self.ida_e_volta()

        self.assertEqual(len(atendimentos.em_andamento_por_atendente), 1)
        em_andamento = atendimentos.em_andamento_por_atendente[2]
        self.assertEqual(em_andamento.id, 4)
        self.assertIs(em_andamento.cliente, clientes.buscar(3))
        self.assertIs(em_andamento.atendente, atendentes.buscar(2))
        self.assertEqual(len(atendimentos.abertos_por_cliente), 4)

    def test_historico_e_pilha_voltam_na_mesma_ordem(self):
        clientes, atendentes, atendimentos, avisos = self.ida_e_volta()

        self.assertEqual(ids(atendimentos.historico), [1, 2])
        self.assertEqual(atendimentos.pilha_desfazer.tamanho(), 2)
        self.assertEqual(atendimentos.pilha_desfazer.topo().id, 2)
        self.assertEqual(atendimentos.historico[0].duracao_segundos(), 300.0)
        self.assertEqual(atendimentos.historico[1].duracao_segundos(), 600.0)

    def test_filas_mantem_a_ordem_de_chamada(self):
        clientes, atendentes, atendimentos, avisos = self.ida_e_volta()

        self.assertEqual(ids(atendimentos.fila_comum.listar()), [3, 6])
        self.assertEqual(ids(atendimentos.fila_prioridade.listar()), [5])

        primeiro = atendimentos.chamar_proximo(1, hora(1, 11, 0))
        atendimentos.finalizar(1, hora(1, 11, 5))
        segundo = atendimentos.chamar_proximo(1, hora(1, 11, 10))
        atendimentos.finalizar(1, hora(1, 11, 15))
        terceiro = atendimentos.chamar_proximo(1, hora(1, 11, 20))

        self.assertEqual([primeiro.id, segundo.id, terceiro.id], [5, 3, 6])

    def test_proximo_id_continua_de_onde_parou(self):
        clientes, atendentes, atendimentos, avisos = self.ida_e_volta()
        novo = atendimentos.abrir(2, hora(1, 11, 0))
        self.assertEqual(novo.id, 7)

    def test_desfazer_funciona_depois_de_carregar(self):
        clientes, atendentes, atendimentos, avisos = self.ida_e_volta()

        desfeito = atendimentos.desfazer_finalizacao()

        self.assertEqual(desfeito.id, 2)
        self.assertEqual(desfeito.estado, "em_andamento")
        self.assertTrue(atendentes.buscar(1).ocupado)
        self.assertEqual(clientes.buscar(2).ultima_atividade, hora(1, 9, 0))
        self.assertEqual(ids(atendimentos.historico), [1])

    def test_cliente_removido_continua_no_historico(self):
        self.atendimentos.remover_cliente(2)
        clientes, atendentes, atendimentos, avisos = self.ida_e_volta()

        self.assertEqual(avisos, [])
        self.assertIsNone(clientes.buscar(2))
        self.assertEqual(clientes.total(), 4)
        self.assertEqual(atendimentos.historico[1].cliente.id, 2)
        self.assertEqual(atendimentos.historico[1].cliente.nome, "Davi")

        with self.assertRaises(ValueError):
            atendimentos.desfazer_finalizacao()
        self.assertEqual(atendimentos.pilha_desfazer.tamanho(), 2)

class TestCarregarArquivosRuins(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.pasta.cleanup()

    def caminho(self, nome):
        return os.path.join(self.pasta.name, nome)

    def test_pasta_inexistente_carrega_sistema_vazio(self):
        pasta = os.path.join(self.pasta.name, "nao_existe")
        clientes, atendentes, atendimentos, avisos = carregar_sistema(pasta)
        self.assertEqual(clientes.total(), 0)
        self.assertEqual(atendentes.total(), 0)
        self.assertEqual(len(atendimentos.historico), 0)
        self.assertEqual(avisos, [])

    def test_sistema_vazio_ida_e_volta(self):
        clientes = ServicoClientes()
        atendentes = ServicoAtendentes()
        atendimentos = ServicoAtendimentos(clientes, atendentes)
        salvar_sistema(self.pasta.name, clientes, atendentes, atendimentos)
        novo_clientes, novo_atendentes, novo_atendimentos, avisos = carregar_sistema(self.pasta.name)

        self.assertEqual(novo_clientes.total(), 0)
        self.assertEqual(novo_atendentes.total(), 0)
        self.assertEqual(novo_atendimentos.proximo_id, 1)
        self.assertEqual(avisos, [])

    def test_linhas_invalidas_de_clientes_viram_avisos(self):
        gravar_csv(
            self.caminho("clientes.csv"),
            ["id", "nome", "telefone", "prioridade", "ultima_atividade"],
            [
                ["1", "Ana", "11999990000", "0", "2026-10-01T09:00:00"],
                ["0", "Zero", "11999990001", "0", "2026-10-01T09:00:00"],
                ["abc", "Letras", "11999990002", "0", ""],
                ["3", "Curta"],
                ["1", "Repetida", "11999990003", "0", "2026-10-01T09:00:00"],
                ["5", "Telefone", "123", "0", "2026-10-01T09:00:00"],
                ["6", "Eva", "11999990004", "0", "2026-10-01T09:00:00"],
            ],
        )

        clientes, atendentes, atendimentos, avisos = carregar_sistema(self.pasta.name)

        self.assertEqual(ids(clientes.listar()), [1, 6])
        self.assertEqual(len(avisos), 5)
        self.assertIn("clientes.csv, linha 3", avisos[0])

    def test_atendimento_aberto_de_cliente_inexistente_vira_aviso(self):
        gravar_csv(
            self.caminho("atendimentos.csv"),
            ["id", "estado", "id_cliente", "nome_cliente", "telefone_cliente",
             "prioridade_cliente", "id_atendente", "hora_entrada", "hora_inicio",
             "hora_fim", "ultima_atividade_anterior"],
            [["1", "aguardando", "99", "Fulano", "11999990000", "0", "",
              "2026-10-01T10:00:00", "", "", ""]],
        )
        clientes, atendentes, atendimentos, avisos = carregar_sistema(self.pasta.name)
        self.assertEqual(len(avisos), 1)
        self.assertEqual(atendimentos.fila_comum.tamanho(), 0)
        self.assertEqual(len(atendimentos.abertos_por_cliente), 0)

    def test_atendimento_em_andamento_sem_atendente_vira_aviso(self):
        gravar_csv(
            self.caminho("clientes.csv"),
            ["id", "nome", "telefone", "prioridade", "ultima_atividade"],
            [["1", "Ana", "11999990000", "0", "2026-10-01T09:00:00"]],
        )
        gravar_csv(
            self.caminho("atendimentos.csv"),
            ["id", "estado", "id_cliente", "nome_cliente", "telefone_cliente",
             "prioridade_cliente", "id_atendente", "hora_entrada", "hora_inicio",
             "hora_fim", "ultima_atividade_anterior"],
            [["1", "em_andamento", "1", "Ana", "11999990000", "0", "",
              "2026-10-01T10:00:00", "2026-10-01T10:05:00", "", ""]],
        )
        clientes, atendentes, atendimentos, avisos = carregar_sistema(self.pasta.name)
        self.assertEqual(len(avisos), 1)
        self.assertEqual(len(atendimentos.em_andamento_por_atendente), 0)
        self.assertEqual(len(atendimentos.abertos_por_cliente), 0)