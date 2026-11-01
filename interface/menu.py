from interface.apresentacao import (
    texto_da_duracao,
    texto_da_prioridade,
    texto_do_atendente,
    texto_do_atendimento,
    texto_do_cliente,
)
from interface.entrada import (
    converter_data,
    converter_inteiro,
    converter_texto,
    ler_valor,
    validar_nao_negativo,
)
from modelos.cliente import validar_prioridade, validar_telefone
from modelos.validacoes import validar_id, validar_nome
from persistencia.exportacao import (    # NOVO
    exportar_alertas,
    exportar_atendimentos,
    exportar_tempo_medio,
    exportar_top_clientes,
)
from servicos.registro import obter_logger

LOGGER = obter_logger()

def ler_id(pergunta, entrada, saida):
    return ler_valor(pergunta, converter_inteiro, validar_id, entrada, saida)

def mostrar_atendimentos(atendimentos, texto_vazio, saida):
    if len(atendimentos) == 0:
        saida("  " + texto_vazio)
    for atendimento in atendimentos:
        saida("  " + texto_do_atendimento(atendimento))

def cadastrar_cliente(sistema, entrada, saida):
    id_cliente = ler_id("ID do cliente: ", entrada, saida)

    if sistema.clientes.buscar(id_cliente) is not None:
        raise ValueError("Já existe um cliente com o ID " + str(id_cliente) + ".")

    nome = ler_valor("Nome: ", converter_texto, validar_nome, entrada, saida)
    telefone = ler_valor(
        "Telefone (só números, com DDD): ", converter_texto, validar_telefone, entrada, saida
    )
    prioridade = ler_valor(
        "Prioridade (0 comum, 1 preferencial, 2 urgente): ",
        converter_inteiro, validar_prioridade, entrada, saida,
    )

    sistema.clientes.cadastrar(id_cliente, nome, telefone, prioridade)
    LOGGER.info("Cliente %s cadastrado", id_cliente)
    saida("Cliente cadastrado!")

def buscar_cliente(sistema, entrada, saida):
    id_cliente = ler_id("ID do cliente: ", entrada, saida)
    cliente = sistema.clientes.buscar(id_cliente)
    if cliente is None:
        saida("Cliente não encontrado.")
    else:
        saida(texto_do_cliente(cliente))

def listar_clientes(sistema, entrada, saida):
    clientes = sistema.clientes.listar()
    if len(clientes) == 0:
        saida("Nenhum cliente cadastrado.")
    for cliente in clientes:
        saida(texto_do_cliente(cliente))

def remover_cliente(sistema, entrada, saida):
    id_cliente = ler_id("ID do cliente a remover: ", entrada, saida)
    sistema.atendimentos.remover_cliente(id_cliente)
    saida("Cliente removido. O histórico de atendimentos dele foi mantido.")

def remover_inativos(sistema, entrada, saida):
    dias = ler_valor(
        "Remover clientes sem atividade há mais de quantos dias? ",
        converter_inteiro, validar_nao_negativo, entrada, saida,
    )
    removidos = sistema.atendimentos.remover_clientes_inativos(dias)
    if len(removidos) == 0:
        saida("Nenhum cliente inativo encontrado.")
        return
    for cliente in removidos:
        saida("Removido: " + texto_do_cliente(cliente))
    saida(str(len(removidos)) + " cliente(s) removido(s).")

def cadastrar_atendente(sistema, entrada, saida):
    id_atendente = ler_id("ID do atendente: ", entrada, saida)
    if sistema.atendentes.buscar(id_atendente) is not None:
        raise ValueError("Já existe um atendente com o ID " + str(id_atendente) + ".")

    nome = ler_valor("Nome: ", converter_texto, validar_nome, entrada, saida)
    sistema.atendentes.cadastrar(id_atendente, nome)
    LOGGER.info("Atendente %s cadastrado", id_atendente)
    saida("Atendente cadastrado!")

def listar_atendentes(sistema, entrada, saida):
    atendentes = sistema.atendentes.listar()
    if len(atendentes) == 0:
        saida("Nenhum atendente cadastrado.")
    for atendente in atendentes:
        saida(texto_do_atendente(atendente))

def abrir_atendimento(sistema, entrada, saida):
    id_cliente = ler_id("ID do cliente: ", entrada, saida)
    atendimento = sistema.atendimentos.abrir(id_cliente)
    cliente = atendimento.cliente
    saida(
        "Atendimento " + str(atendimento.id) + " aberto: " + cliente.nome
        + " entrou na fila (" + texto_da_prioridade(cliente.prioridade) + ")."
    )

def chamar_proximo(sistema, entrada, saida):
    id_atendente = ler_id("ID do atendente: ", entrada, saida)
    atendimento = sistema.atendimentos.chamar_proximo(id_atendente)
    cliente = atendimento.cliente
    saida(
        "Atendente " + atendimento.atendente.nome + " chama: " + cliente.nome
        + " (atendimento " + str(atendimento.id) + ", "
        + texto_da_prioridade(cliente.prioridade) + ")."
    )

def finalizar_atendimento(sistema, entrada, saida):
    id_atendente = ler_id("ID do atendente: ", entrada, saida)
    atendimento = sistema.atendimentos.finalizar(id_atendente)
    saida(
        "Atendimento " + str(atendimento.id) + " finalizado. Duração: "
        + texto_da_duracao(atendimento.duracao_segundos()) + "."
    )

def desfazer_finalizacao(sistema, entrada, saida):
    atendimento = sistema.atendimentos.desfazer_finalizacao()
    saida(
        "Finalização do atendimento " + str(atendimento.id) + " desfeita: "
        + atendimento.atendente.nome + " voltou a atender "
        + atendimento.cliente.nome + "."
    )

def ver_filas(sistema, entrada, saida):
    fila_prioridade = sistema.atendimentos.fila_prioridade.listar()
    fila_comum = sistema.atendimentos.fila_comum.listar()
    em_atendimento = list(sistema.atendimentos.em_andamento_por_atendente.values())

    saida("Fila de prioridade (na ordem de chamada):")
    mostrar_atendimentos(fila_prioridade, "(ninguém aguardando)", saida)
    saida("Fila comum:")
    mostrar_atendimentos(fila_comum, "(ninguém aguardando)", saida)
    saida("Em atendimento:")
    mostrar_atendimentos(em_atendimento, "(ninguém em atendimento)", saida)

def ver_historico_do_cliente(sistema, entrada, saida):
    id_cliente = ler_id("ID do cliente: ", entrada, saida)
    historico = sistema.atendimentos.historico_do_cliente(id_cliente)
    mostrar_atendimentos(historico, "Nenhum atendimento finalizado para este cliente.", saida)

def mostrar_tempo_medio(sistema, entrada, saida):
    media = sistema.relatorios.tempo_medio_segundos()
    if media is None:
        saida("Ainda não há atendimentos finalizados.")
        return
    total = len(sistema.atendimentos.historico)
    saida(
        "Tempo médio de atendimento: " + texto_da_duracao(media)
        + " (" + str(total) + " atendimento(s))."
    )

def mostrar_top_clientes(sistema, entrada, saida):
    top = sistema.relatorios.top_clientes()
    if len(top) == 0:
        saida("Ainda não há atendimentos finalizados.")
        return
    posicao = 0
    for cliente, total in top:
        posicao = posicao + 1
        saida(
            str(posicao) + "º " + cliente.nome + " (ID " + str(cliente.id) + "): "
            + str(total) + " atendimento(s)"
        )

def mostrar_atendimentos_por_data(sistema, entrada, saida):
    inicio = ler_valor(
        "Data inicial (DD/MM/AAAA): ", converter_data, entrada=entrada, saida=saida
    )
    fim = ler_valor(
        "Data final (DD/MM/AAAA): ", converter_data, entrada=entrada, saida=saida
    )
    encontrados = sistema.relatorios.filtrar_por_data(inicio, fim)
    mostrar_atendimentos(encontrados, "Nenhum atendimento no período.", saida)

def mostrar_alertas(sistema, entrada, saida):
    minutos = ler_valor(
        "Alertar quem espera há mais de quantos minutos? ",
        converter_inteiro, validar_nao_negativo, entrada, saida,
    )
    alertas = sistema.relatorios.alertas_de_espera(minutos * 60)
    if len(alertas) == 0:
        saida("Nenhum cliente esperando há mais de " + str(minutos) + " minuto(s).")
        return
    for atendimento, espera in alertas:
        saida(
            "ALERTA: " + atendimento.cliente.nome + " (atendimento " + str(atendimento.id)
            + ", " + texto_da_prioridade(atendimento.cliente.prioridade)
            + ") espera há " + texto_da_duracao(espera)
        )

def exportar_relatorios(sistema, entrada, saida):
    minutos = ler_valor(
        "Limite de espera para o relatório de alertas (minutos): ",
        converter_inteiro, validar_nao_negativo, entrada, saida,
    )
    relatorios = sistema.relatorios
    historico = sistema.atendimentos.historico

    exportar_tempo_medio(
        sistema.caminho_de_exportacao("tempo_medio.csv"),
        relatorios.tempo_medio_segundos(),
        len(historico),
    )
    exportar_top_clientes(
        sistema.caminho_de_exportacao("top_clientes.csv"),
        relatorios.top_clientes(),
    )
    exportar_atendimentos(
        sistema.caminho_de_exportacao("atendimentos.csv"),
        historico,
    )
    exportar_alertas(
        sistema.caminho_de_exportacao("alertas_de_espera.csv"),
        relatorios.alertas_de_espera(minutos * 60),
    )

    LOGGER.info("Relatórios exportados para %s", sistema.pasta_exportacao)
    saida("Relatórios exportados para a pasta: " + sistema.pasta_exportacao)

def salvar_agora(sistema, entrada, saida):
    sistema.salvar()
    saida("Dados salvos.")

OPCOES = [
    ("1", "Cadastrar cliente", cadastrar_cliente),
    ("2", "Buscar cliente por ID", buscar_cliente),
    ("3", "Listar clientes", listar_clientes),
    ("4", "Remover cliente", remover_cliente),
    ("5", "Remover clientes inativos", remover_inativos),
    ("6", "Cadastrar atendente", cadastrar_atendente),
    ("7", "Listar atendentes", listar_atendentes),
    ("8", "Abrir atendimento (entrar na fila)", abrir_atendimento),
    ("9", "Chamar próximo cliente", chamar_proximo),
    ("10", "Finalizar atendimento", finalizar_atendimento),
    ("11", "Desfazer última finalização", desfazer_finalizacao),
    ("12", "Ver filas e atendimentos em andamento", ver_filas),
    ("13", "Histórico de atendimentos de um cliente", ver_historico_do_cliente),
    ("14", "Tempo médio de atendimento", mostrar_tempo_medio),
    ("15", "Cinco clientes mais atendidos", mostrar_top_clientes),
    ("16", "Atendimentos por data", mostrar_atendimentos_por_data),
    ("17", "Alertas de espera elevada", mostrar_alertas),
    ("18", "Exportar relatórios em CSV", exportar_relatorios),
    ("19", "Salvar agora", salvar_agora),
]

def mostrar_menu(saida):
    saida("")
    saida("===== Sistema de Atendimento e Análise =====")
    for numero, descricao, acao in OPCOES:
        saida(numero + " - " + descricao)
    saida("0 - Salvar e sair")

def achar_acao(opcao):
    for numero, descricao, acao in OPCOES:
        if numero == opcao:
            return acao
    return None

def executar_acao(acao, sistema, entrada, saida):
    try:
        acao(sistema, entrada, saida)
    except ValueError as erro:
        saida("Não foi possível concluir: " + str(erro))
        LOGGER.warning("Operação recusada: %s", erro)
    except OSError as erro:
        saida("Erro ao acessar arquivos: " + str(erro))
        LOGGER.error("Falha de arquivo: %s", erro)

def salvar_e_sair(sistema, saida):
    try:
        sistema.salvar()
    except OSError as erro:
        saida("Não foi possível salvar os dados: " + str(erro))
        LOGGER.error("Falha ao salvar: %s", erro)
        return False
    saida("Dados salvos. Até logo!")
    return True

def executar_menu(sistema, entrada=input, saida=print):
    while True:
        mostrar_menu(saida)
        opcao = entrada("Escolha: ").strip()

        if opcao == "0":
            if salvar_e_sair(sistema, saida):
                return
        else:
            acao = achar_acao(opcao)
            if acao is None:
                saida("Opção inválida.")
            else:
                executar_acao(acao, sistema, entrada, saida)