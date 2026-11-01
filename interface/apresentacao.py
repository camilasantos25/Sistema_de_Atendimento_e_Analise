from modelos.atendimento import (
    ESTADO_AGUARDANDO,
    ESTADO_EM_ANDAMENTO,
    ESTADO_FINALIZADO,
)
from modelos.cliente import (
    PRIORIDADE_COMUM,
    PRIORIDADE_PREFERENCIAL,
    PRIORIDADE_URGENTE,
)

NOMES_PRIORIDADE = {
    PRIORIDADE_COMUM: "comum",
    PRIORIDADE_PREFERENCIAL: "preferencial",
    PRIORIDADE_URGENTE: "urgente",
}

NOMES_ESTADO = {
    ESTADO_AGUARDANDO: "aguardando",
    ESTADO_EM_ANDAMENTO: "em andamento",
    ESTADO_FINALIZADO: "finalizado",
}

def texto_da_prioridade(prioridade):
    return NOMES_PRIORIDADE[prioridade]

def texto_do_cliente(cliente):
    return (
        "ID " + str(cliente.id)
        + " | " + cliente.nome
        + " | " + cliente.telefone
        + " | " + texto_da_prioridade(cliente.prioridade)
    )

def texto_da_duracao(segundos):
    total = round(segundos)
    minutos = total // 60
    resto = total % 60
    if minutos == 0:
        return str(resto) + " s"
    return str(minutos) + " min " + str(resto) + " s"

def texto_da_hora(momento):
    return momento.strftime("%d/%m/%Y %H:%M")

def texto_do_atendente(atendente):
    situacao = "livre"
    if atendente.ocupado:
        situacao = "ocupado"
    return "ID " + str(atendente.id) + " | " + atendente.nome + " | " + situacao

def texto_do_atendimento(atendimento):
    texto = (
        "Atendimento " + str(atendimento.id)
        + " | " + atendimento.cliente.nome
        + " | " + NOMES_ESTADO[atendimento.estado]
        + " | entrada " + texto_da_hora(atendimento.hora_entrada)
    )
    if atendimento.atendente is not None:
        texto = texto + " | atendente " + atendimento.atendente.nome
    duracao = atendimento.duracao_segundos()
    if duracao is not None:
        texto = texto + " | duração " + texto_da_duracao(duracao)
    return texto