from datetime import datetime, timedelta
from estruturas.fila import Fila
from estruturas.fila_prioridade import FilaPrioridade
from estruturas.pilha import Pilha
from modelos.atendimento import (
    Atendimento,
    ESTADO_AGUARDANDO,
    ESTADO_EM_ANDAMENTO,
    ESTADO_FINALIZADO,
)
from modelos.cliente import PRIORIDADE_COMUM, PRIORIDADE_URGENTE

def hora_ou_agora(agora):
    if agora is None:
        return datetime.now()
    return agora

class ServicoAtendimentos:
    def __init__(self, servico_clientes, servico_atendentes):
        self.servico_clientes = servico_clientes
        self.servico_atendentes = servico_atendentes
        self.fila_comum = Fila()
        self.fila_prioridade = FilaPrioridade(PRIORIDADE_URGENTE)
        self.abertos_por_cliente = {}
        self.em_andamento_por_atendente = {}
        self.historico = []
        self.pilha_desfazer = Pilha()
        self.proximo_id = 1

    def abrir(self, id_cliente, agora=None):
        cliente = self.servico_clientes.buscar(id_cliente)
        if cliente is None:
            raise ValueError("Cliente não encontrado.")
        if id_cliente in self.abertos_por_cliente:
            raise ValueError("O cliente já tem um atendimento aberto.")

        atendimento = Atendimento(self.proximo_id, cliente, hora_ou_agora(agora))
        self.proximo_id = self.proximo_id + 1

        if cliente.prioridade == PRIORIDADE_COMUM:
            self.fila_comum.entrar(atendimento)
        else:
            self.fila_prioridade.entrar(atendimento, cliente.prioridade)

        self.abertos_por_cliente[id_cliente] = atendimento
        return atendimento

    def chamar_proximo(self, id_atendente, agora=None):
        atendente = self.servico_atendentes.buscar(id_atendente)
        if atendente is None:
            raise ValueError("Atendente não encontrado.")
        if atendente.ocupado:
            raise ValueError("O atendente já está atendendo alguém.")

        if not self.fila_prioridade.esta_vazia():
            atendimento = self.fila_prioridade.sair()
        elif not self.fila_comum.esta_vazia():
            atendimento = self.fila_comum.sair()
        else:
            raise ValueError("Não há clientes aguardando.")

        atendimento.atendente = atendente
        atendimento.estado = ESTADO_EM_ANDAMENTO
        atendimento.hora_inicio = hora_ou_agora(agora)
        atendente.ocupado = True
        self.em_andamento_por_atendente[id_atendente] = atendimento
        return atendimento

    def finalizar(self, id_atendente, agora=None):
        atendimento = self.em_andamento_por_atendente.get(id_atendente)
        if atendimento is None:
            raise ValueError("Não há atendimento em andamento para este atendente.")

        atendimento.estado = ESTADO_FINALIZADO
        atendimento.hora_fim = hora_ou_agora(agora)
        atendimento.atendente.ocupado = False

        atendimento.ultima_atividade_anterior = atendimento.cliente.ultima_atividade
        atendimento.cliente.ultima_atividade = atendimento.hora_fim

        del self.em_andamento_por_atendente[id_atendente]
        del self.abertos_por_cliente[atendimento.cliente.id]
        self.historico.append(atendimento)
        self.pilha_desfazer.empilhar(atendimento)
        return atendimento

    def desfazer_finalizacao(self):
        if self.pilha_desfazer.esta_vazia():
            raise ValueError("Não há finalização para desfazer.")

        atendimento = self.pilha_desfazer.topo()
        atendente = atendimento.atendente
        cliente = atendimento.cliente

        if atendente.ocupado:
            raise ValueError("O atendente já está atendendo outro cliente.")
        if self.servico_clientes.buscar(cliente.id) is not cliente:
            raise ValueError("O cliente deste atendimento foi removido do cadastro.")
        if cliente.id in self.abertos_por_cliente:
            raise ValueError("O cliente já tem outro atendimento aberto.")

        self.pilha_desfazer.desempilhar()
        self.historico.pop()

        atendimento.estado = ESTADO_EM_ANDAMENTO
        atendimento.hora_fim = None
        atendente.ocupado = True
        cliente.ultima_atividade = atendimento.ultima_atividade_anterior
        self.em_andamento_por_atendente[atendente.id] = atendimento
        self.abertos_por_cliente[atendimento.cliente.id] = atendimento
        return atendimento

    def historico_do_cliente(self, id_cliente):
        resultado = []
        for atendimento in self.historico:
            if atendimento.cliente.id == id_cliente:
                resultado.append(atendimento)
        return resultado

    def remover_cliente(self, id_cliente):
        if self.servico_clientes.buscar(id_cliente) is None:
            raise ValueError("Cliente não encontrado.")
        if id_cliente in self.abertos_por_cliente:
            raise ValueError("O cliente tem atendimento aberto e não pode ser removido.")
        return self.servico_clientes.remover(id_cliente)

    def remover_clientes_inativos(self, dias, agora=None):
        if dias < 0:
            raise ValueError("O número de dias não pode ser negativo.")

        limite = hora_ou_agora(agora) - timedelta(days=dias)

        def esta_inativo(cliente):
            sem_atendimento_aberto = cliente.id not in self.abertos_por_cliente
            return sem_atendimento_aberto and cliente.ultima_atividade < limite

        return self.servico_clientes.remover_se(esta_inativo)