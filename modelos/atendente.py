from modelos.validacoes import validar_id, validar_nome

class Atendente:
    def __init__(self, id_atendente, nome):
        validar_id(id_atendente)
        validar_nome(nome)

        self.id = id_atendente
        self.nome = nome.strip()