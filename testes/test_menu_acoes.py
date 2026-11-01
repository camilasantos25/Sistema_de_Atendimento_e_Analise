import csv
import os
import tempfile
import unittest
from datetime import datetime
from interface.menu import executar_menu
from interface.sistema import Sistema
from testes.apoio import entradas_falsas

def hora(dia, horas, minutos):
    return datetime(2026, 10, dia, horas, minutos, 0)

def alguma_comeca_com(textos, prefixo):
    for texto in textos:
        if texto.startswith(prefixo):
            return True
    return False

def mensagens_do_log(capturado):
    resultado = []
    for registro in capturado.records:
        resultado.append(registro.getMessage())
    return resultado

def ler_csv(caminho):
    with open(caminho, "r", newline="", encoding="utf-8") as arquivo:
        return list(csv.reader(arquivo))

class BaseDoMenu(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.sistema = Sistema(self.pasta.name)
        self.saida = []
        self.sistema.clientes.cadastrar(1, "Ana", "11999990000", 0)
        self.sistema.clientes.cadastrar(2, "Davi", "11999990001", 0)
        self.sistema.clientes.cadastrar(3, "Eva", "11999990002", 2)
        self.sistema.atendentes.cadastrar(1, "Carla")
        self.sistema.atendentes.cadastrar(2, "Paulo")

    def tearDown(self):
        self.pasta.cleanup()

    def rodar(self, respostas):
        executar_menu(self.sistema, entradas_falsas(respostas), self.saida.append)

    def atender(self, id_cliente, dia, minuto_inicio, minuto_fim):
        self.sistema.atendimentos.abrir(id_cliente, hora(dia, 10, minuto_inicio))
        self.sistema.atendimentos.chamar_proximo(1, hora(dia, 10, minuto_inicio))
        self.sistema.atendimentos.finalizar(1, hora(dia, 10, minuto_fim))

class TestMenuAtendentes(BaseDoMenu):
    def test_cadastrar_atendente(self):
        self.rodar(["6", "3", "Joana", "0"])
        self.assertEqual(self.sistema.atendentes.buscar(3).nome, "Joana")
        self.assertIn("Atendente cadastrado!", self.saida)

    def test_atendente_duplicado_e_recusado(self):
        self.rodar(["6", "1", "0"])
        self.assertIn(
            "Não foi possível concluir: Já existe um atendente com o ID 1.", self.saida
        )
        self.assertEqual(self.sistema.atendentes.total(), 2)

    def test_listar_atendentes_mostra_livre_e_ocupado(self):
        self.sistema.atendimentos.abrir(1, hora(1, 10, 0))
        self.sistema.atendimentos.chamar_proximo(1, hora(1, 10, 0))
        self.rodar(["7", "0"])
        self.assertIn("ID 1 | Carla | ocupado", self.saida)
        self.assertIn("ID 2 | Paulo | livre", self.saida)

    def test_listar_sem_atendentes(self):
        vazio = Sistema(os.path.join(self.pasta.name, "vazio"))
        executar_menu(vazio, entradas_falsas(["7", "0"]), self.saida.append)
        self.assertIn("Nenhum atendente cadastrado.", self.saida)

class TestMenuRemocoes(BaseDoMenu):
    def test_remover_cliente(self):
        self.rodar(["4", "2", "0"])
        self.assertIsNone(self.sistema.clientes.buscar(2))
        self.assertIn(
            "Cliente removido. O histórico de atendimentos dele foi mantido.", self.saida
        )

    def test_remover_cliente_inexistente(self):
        self.rodar(["4", "99", "0"])
        self.assertIn("Não foi possível concluir: Cliente não encontrado.", self.saida)

    def test_remover_cliente_com_atendimento_aberto_e_recusado(self):
        self.sistema.atendimentos.abrir(1, hora(1, 10, 0))
        self.rodar(["4", "1", "0"])
        self.assertIn(
            "Não foi possível concluir: O cliente tem atendimento aberto"
            " e não pode ser removido.",
            self.saida,
        )
        self.assertIsNotNone(self.sistema.clientes.buscar(1))

    def test_remover_inativos(self):
        self.sistema.clientes.cadastrar(
            10, "Velho", "11999990010", 0, datetime(2020, 1, 1, 9, 0, 0)
        )
        self.rodar(["5", "30", "0"])

        self.assertIsNone(self.sistema.clientes.buscar(10))
        self.assertIsNotNone(self.sistema.clientes.buscar(1))
        self.assertIn("Removido: ID 10 | Velho | 11999990010 | comum", self.saida)
        self.assertIn("1 cliente(s) removido(s).", self.saida)
        self.assertEqual(self.sistema.clientes.total(), 3)
        self.assertEqual(self.sistema.clientes.total_ativos(), 3)

    def test_nenhum_cliente_inativo(self):
        self.rodar(["5", "30", "0"])
        self.assertIn("Nenhum cliente inativo encontrado.", self.saida)
        self.assertEqual(self.sistema.clientes.total(), 3)

    def test_dias_invalidos_repetem_a_pergunta(self):
        self.rodar(["5", "-1", "abc", "30", "0"])
        self.assertIn("Entrada inválida: O valor não pode ser negativo.", self.saida)
        self.assertIn("Entrada inválida: Digite um número inteiro.", self.saida)


class TestMenuAtendimentos(BaseDoMenu):
    def test_abrir_atendimento(self):
        self.rodar(["8", "1", "0"])
        self.assertIn("Atendimento 1 aberto: Ana entrou na fila (comum).", self.saida)
        self.assertEqual(self.sistema.atendimentos.fila_comum.tamanho(), 1)

    def test_abrir_cliente_inexistente(self):
        self.rodar(["8", "99", "0"])
        self.assertIn("Não foi possível concluir: Cliente não encontrado.", self.saida)

    def test_abrir_duas_vezes_e_recusado(self):
        self.rodar(["8", "1", "8", "1", "0"])
        self.assertIn(
            "Não foi possível concluir: O cliente já tem um atendimento aberto.", self.saida
        )
        self.assertEqual(self.sistema.atendimentos.fila_comum.tamanho(), 1)

    def test_chamar_respeita_a_prioridade(self):
        self.rodar(["8", "1", "8", "3", "9", "1", "0"])
        self.assertIn("Atendente Carla chama: Eva (atendimento 2, urgente).", self.saida)
        self.assertEqual(self.sistema.atendimentos.fila_comum.tamanho(), 1)

    def test_chamar_sem_ninguem_aguardando(self):
        self.rodar(["9", "1", "0"])
        self.assertIn("Não foi possível concluir: Não há clientes aguardando.", self.saida)

    def test_chamar_com_atendente_ocupado(self):
        self.rodar(["8", "1", "8", "2", "9", "1", "9", "1", "0"])
        self.assertIn(
            "Não foi possível concluir: O atendente já está atendendo alguém.", self.saida
        )
        self.assertEqual(self.sistema.atendimentos.fila_comum.tamanho(), 1)

    def test_finalizar(self):
        self.rodar(["8", "1", "9", "1", "10", "1", "0"])
        self.assertTrue(alguma_comeca_com(self.saida, "Atendimento 1 finalizado. Duração: "))
        self.assertEqual(len(self.sistema.atendimentos.historico), 1)
        self.assertFalse(self.sistema.atendentes.buscar(1).ocupado)

    def test_finalizar_sem_atendimento_em_andamento(self):
        self.rodar(["10", "1", "0"])
        self.assertIn(
            "Não foi possível concluir: Não há atendimento em andamento"
            " para este atendente.",
            self.saida,
        )

    def test_desfazer(self):
        self.rodar(["8", "1", "9", "1", "10", "1", "11", "0"])
        self.assertIn(
            "Finalização do atendimento 1 desfeita: Carla voltou a atender Ana.", self.saida
        )
        self.assertTrue(self.sistema.atendentes.buscar(1).ocupado)
        self.assertEqual(len(self.sistema.atendimentos.historico), 0)

    def test_desfazer_sem_nada_para_desfazer(self):
        self.rodar(["11", "0"])
        self.assertIn(
            "Não foi possível concluir: Não há finalização para desfazer.", self.saida
        )

class TestMenuConsultas(BaseDoMenu):
    def test_ver_filas_e_em_atendimento(self):
        self.sistema.atendimentos.abrir(1, hora(1, 10, 0))
        self.sistema.atendimentos.abrir(3, hora(1, 10, 5))
        self.sistema.atendimentos.abrir(2, hora(1, 10, 10))
        self.sistema.atendimentos.chamar_proximo(1, hora(1, 10, 20))

        self.rodar(["12", "0"])

        inicio = self.saida.index("Fila de prioridade (na ordem de chamada):")
        self.assertEqual(
            self.saida[inicio:inicio + 7],
            [
                "Fila de prioridade (na ordem de chamada):",
                "  (ninguém aguardando)",
                "Fila comum:",
                "  Atendimento 1 | Ana | aguardando | entrada 01/10/2026 10:00",
                "  Atendimento 3 | Davi | aguardando | entrada 01/10/2026 10:10",
                "Em atendimento:",
                "  Atendimento 2 | Eva | em andamento | entrada 01/10/2026 10:05"
                " | atendente Carla",
            ],
        )

    def test_ver_filas_vazias(self):
        self.rodar(["12", "0"])
        self.assertEqual(self.saida.count("  (ninguém aguardando)"), 2)
        self.assertEqual(self.saida.count("  (ninguém em atendimento)"), 1)

    def test_historico_do_cliente(self):
        self.atender(1, 1, 0, 5)
        self.rodar(["13", "1", "13", "2", "0"])
        self.assertIn(
            "  Atendimento 1 | Ana | finalizado | entrada 01/10/2026 10:00"
            " | atendente Carla | duração 5 min 0 s",
            self.saida,
        )
        self.assertIn("  Nenhum atendimento finalizado para este cliente.", self.saida)

class TestMenuRelatorios(BaseDoMenu):
    def test_tempo_medio_sem_historico(self):
        self.rodar(["14", "0"])
        self.assertIn("Ainda não há atendimentos finalizados.", self.saida)

    def test_tempo_medio(self):
        self.atender(1, 1, 0, 5)
        self.atender(2, 1, 10, 20)
        self.rodar(["14", "0"])
        self.assertIn(
            "Tempo médio de atendimento: 7 min 30 s (2 atendimento(s)).", self.saida
        )

    def test_top_clientes(self):
        self.atender(3, 1, 0, 5)
        self.atender(2, 1, 10, 15)
        self.atender(1, 1, 20, 25)
        self.atender(2, 1, 30, 35)
        self.rodar(["15", "0"])

        inicio = self.saida.index("1º Davi (ID 2): 2 atendimento(s)")
        self.assertEqual(
            self.saida[inicio:inicio + 3],
            [
                "1º Davi (ID 2): 2 atendimento(s)",
                "2º Ana (ID 1): 1 atendimento(s)",
                "3º Eva (ID 3): 1 atendimento(s)",
            ],
        )

    def test_top_clientes_sem_historico(self):
        self.rodar(["15", "0"])
        self.assertIn("Ainda não há atendimentos finalizados.", self.saida)

    def test_filtro_por_data(self):
        self.atender(1, 1, 0, 5)
        self.atender(2, 2, 0, 5)
        self.rodar(["16", "01/10/2026", "01/10/2026", "0"])

        self.assertIn(
            "  Atendimento 1 | Ana | finalizado | entrada 01/10/2026 10:00"
            " | atendente Carla | duração 5 min 0 s",
            self.saida,
        )
        for linha in self.saida:
            self.assertNotIn("Davi", linha)

    def test_filtro_sem_resultados(self):
        self.atender(1, 1, 0, 5)
        self.rodar(["16", "10/10/2026", "20/10/2026", "0"])
        self.assertIn("  Nenhum atendimento no período.", self.saida)

    def test_data_invalida_repete_a_pergunta(self):
        self.rodar(["16", "31/02/2026", "01/10/2026", "01/10/2026", "0"])
        self.assertIn(
            "Entrada inválida: Digite a data no formato DD/MM/AAAA, por exemplo 25/10/2026.",
            self.saida,
        )

    def test_data_inicial_depois_da_final(self):
        self.rodar(["16", "05/10/2026", "01/10/2026", "0"])
        self.assertIn(
            "Não foi possível concluir: A data inicial não pode ser depois da final.",
            self.saida,
        )

    def test_alertas_sem_ninguem_esperando(self):
        self.rodar(["17", "30", "0"])
        self.assertIn("Nenhum cliente esperando há mais de 30 minuto(s).", self.saida)

    def test_alertas_com_espera_antiga(self):
        self.sistema.atendimentos.abrir(1, datetime(2020, 1, 1, 10, 0, 0))
        self.rodar(["17", "30", "0"])
        self.assertTrue(
            alguma_comeca_com(self.saida, "ALERTA: Ana (atendimento 1, comum) espera há ")
        )

    def test_alertas_limite_invalido(self):
        self.rodar(["17", "-5", "30", "0"])
        self.assertIn("Entrada inválida: O valor não pode ser negativo.", self.saida)

class TestMenuArquivos(BaseDoMenu):
    def test_exportar_cria_os_quatro_arquivos(self):
        with self.assertLogs("atendimento", level="INFO") as capturado:
            self.rodar(["18", "30", "0"])

        pasta_relatorios = os.path.join(self.pasta.name, "relatorios")
        for nome in [
            "tempo_medio.csv", "top_clientes.csv",
            "atendimentos.csv", "alertas_de_espera.csv",
        ]:
            self.assertTrue(os.path.exists(os.path.join(pasta_relatorios, nome)))

        self.assertTrue(
            alguma_comeca_com(self.saida, "Relatórios exportados para a pasta: ")
        )
        self.assertTrue(
            alguma_comeca_com(mensagens_do_log(capturado), "Relatórios exportados para ")
        )
        self.assertEqual(
            ler_csv(os.path.join(pasta_relatorios, "tempo_medio.csv")),
            [["total_atendimentos", "tempo_medio_segundos"], ["0", ""]],
        )

    def test_exportar_com_historico(self):
        self.atender(1, 1, 0, 5)
        self.rodar(["18", "30", "0"])

        linhas = ler_csv(os.path.join(self.pasta.name, "relatorios", "atendimentos.csv"))
        self.assertEqual(len(linhas), 2)
        self.assertEqual(linhas[1][0], "1")
        self.assertEqual(linhas[1][2], "Ana")

    def test_falha_de_arquivo_na_exportacao(self):
        caminho_ocupado = os.path.join(self.pasta.name, "ocupado")
        with open(caminho_ocupado, "w", encoding="utf-8") as arquivo:
            arquivo.write("x")
        sistema = Sistema(self.pasta.name, caminho_ocupado)

        with self.assertLogs("atendimento", level="ERROR") as capturado:
            executar_menu(sistema, entradas_falsas(["18", "30", "0"]), self.saida.append)

        self.assertTrue(alguma_comeca_com(self.saida, "Erro ao acessar arquivos:"))
        self.assertTrue(alguma_comeca_com(mensagens_do_log(capturado), "Falha de arquivo:"))
        self.assertIn("Dados salvos. Até logo!", self.saida)

    def test_salvar_agora(self):
        self.rodar(["19", "0"])
        self.assertIn("Dados salvos.", self.saida)
        self.assertTrue(os.path.exists(os.path.join(self.pasta.name, "clientes.csv")))

    def test_caminho_de_exportacao_cria_a_pasta(self):
        caminho = self.sistema.caminho_de_exportacao("a.csv")
        self.assertEqual(caminho, os.path.join(self.pasta.name, "relatorios", "a.csv"))
        self.assertTrue(os.path.isdir(os.path.join(self.pasta.name, "relatorios")))