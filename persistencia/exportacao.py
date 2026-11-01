import csv

def gravar_csv(caminho, cabecalho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(cabecalho)
        for linha in linhas:
            escritor.writerow(linha)

def texto_de_data_hora(valor):
    if valor is None:
        return ""
    return valor.isoformat()

def exportar_tempo_medio(caminho, tempo_medio, total_atendimentos):
    gravar_csv(
        caminho,
        ["total_atendimentos", "tempo_medio_segundos"],
        [[total_atendimentos, tempo_medio]],
    )

def exportar_top_clientes(caminho, top):
    linhas = []
    posicao = 0
    for cliente, total in top:
        posicao = posicao + 1
        linhas.append([posicao, cliente.id, cliente.nome, total])

    gravar_csv(
        caminho,
        ["posicao", "id_cliente", "nome_cliente", "total_atendimentos"],
        linhas,
    )

def exportar_atendimentos(caminho, atendimentos):
    linhas = []
    for atendimento in atendimentos:
        linhas.append([
            atendimento.id,
            atendimento.cliente.id,
            atendimento.cliente.nome,
            atendimento.atendente.id,
            atendimento.atendente.nome,
            atendimento.hora_inicio.date().isoformat(),
            texto_de_data_hora(atendimento.hora_entrada),
            texto_de_data_hora(atendimento.hora_inicio),
            texto_de_data_hora(atendimento.hora_fim),
            atendimento.espera_segundos(),
            atendimento.duracao_segundos(),
        ])

    gravar_csv(
        caminho,
        [
            "id_atendimento",
            "id_cliente",
            "nome_cliente",
            "id_atendente",
            "nome_atendente",
            "data",
            "hora_entrada",
            "hora_inicio",
            "hora_fim",
            "espera_segundos",
            "duracao_segundos",
        ],
        linhas,
    )

def exportar_alertas(caminho, alertas):
    linhas = []
    for atendimento, espera in alertas:
        linhas.append([
            atendimento.id,
            atendimento.cliente.id,
            atendimento.cliente.nome,
            atendimento.cliente.prioridade,
            texto_de_data_hora(atendimento.hora_entrada),
            espera,
        ])

    gravar_csv(
        caminho,
        [
            "id_atendimento",
            "id_cliente",
            "nome_cliente",
            "prioridade",
            "hora_entrada",
            "espera_segundos",
        ],
        linhas,
    )