ESTADO_AGUARDANDO = "aguardando"
ESTADO_EM_ANDAMENTO = "em_andamento"
ESTADO_FINALIZADO = "finalizado"

class Atendimento:
    def __init__(self, id_atendimento, cliente, hora_entrada):
        self.id = id_atendimento
        self.cliente = cliente
        self.atendente = None
        self.estado = ESTADO_AGUARDANDO
        self.hora_entrada = hora_entrada
        self.hora_inicio = None
        self.hora_fim = None

    def duracao_segundos(self):
        if self.hora_inicio is None or self.hora_fim is None:
            return None
        return (self.hora_fim - self.hora_inicio).total_seconds()

    def espera_segundos(self):
        if self.hora_inicio is None:
            return None
        return (self.hora_inicio - self.hora_entrada).total_seconds()