from datetime import datetime
from modelos.validacoes import validar_id, validar_nome

PRIORIDADE_COMUM = 0
PRIORIDADE_PREFERENCIAL = 1
PRIORIDADE_URGENTE = 2

PRIORIDADES_VALIDAS = (
    PRIORIDADE_COMUM,
    PRIORIDADE_PREFERENCIAL,
    PRIORIDADE_URGENTE
)

def validar_telefone(telefone):
    if not telefone.isdigit():
        raise ValueError("O telefone deve ter apenas números.")
    if len(telefone) < 10 or len(telefone) > 11:
        raise ValueError("O telefone deve ter 10 ou 11 dígitos (com DDD).")

def validar_prioridade(prioridade):
    if prioridade not in PRIORIDADES_VALIDAS:
        raise ValueError("Prioridade inválida (use 0, 1 ou 2).")

class Cliente:
    def __init__(self, id_cliente, nome, telefone, prioridade, data_cadastro=None):
        validar_id(id_cliente)
        validar_nome(nome)
        validar_telefone(telefone)
        validar_prioridade(prioridade)

        if data_cadastro is None:
            data_cadastro = datetime.now()

        self.id = id_cliente
        self.nome = nome.strip()
        self.telefone = telefone
        self.prioridade = prioridade
        self.ultima_atividade = data_cadastro