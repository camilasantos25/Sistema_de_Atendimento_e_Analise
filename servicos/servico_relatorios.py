from estruturas.ordenacao import insertion_sort, merge_sort
from servicos.servico_atendimentos import hora_ou_agora

def id_do_par(par):
    return par[0].id

def menos_o_numero(par):
    return -par[1]

def hora_de_inicio(atendimento):
    return atendimento.hora_inicio

class ServicoRelatorios:
    def __init__(self, servico_atendimentos):
        self.servico_atendimentos = servico_atendimentos

    def tempo_medio_segundos(self):
        historico = self.servico_atendimentos.historico
        if len(historico) == 0:
            return None

        soma = 0
        for atendimento in historico:
            soma = soma + atendimento.duracao_segundos()
        return soma / len(historico)

    def top_clientes(self, quantidade=5):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        contagem = {}
        for atendimento in self.servico_atendimentos.historico:
            cliente = atendimento.cliente
            registro = contagem.get(cliente.id)
            if registro is None:
                contagem[cliente.id] = [cliente, 1]
            else:
                registro[1] = registro[1] + 1

        pares = list(contagem.values())
        pares = merge_sort(pares, id_do_par)
        pares = merge_sort(pares, menos_o_numero)
        return pares[:quantidade]

    def filtrar_por_data(self, data_inicio, data_fim):
        if data_inicio > data_fim:
            raise ValueError("A data inicial não pode ser depois da final.")

        encontrados = []
        for atendimento in self.servico_atendimentos.historico:
            dia = atendimento.hora_inicio.date()
            if data_inicio <= dia and dia <= data_fim:
                encontrados.append(atendimento)

        return insertion_sort(encontrados, hora_de_inicio)

    def alertas_de_espera(self, limite_segundos, agora=None):
        if limite_segundos < 0:
            raise ValueError("O limite não pode ser negativo.")

        agora = hora_ou_agora(agora)
        fila_prioridade = self.servico_atendimentos.fila_prioridade
        fila_comum = self.servico_atendimentos.fila_comum
        aguardando = fila_prioridade.listar() + fila_comum.listar()

        alertas = []
        for atendimento in aguardando:
            espera = (agora - atendimento.hora_entrada).total_seconds()
            if espera > limite_segundos:
                alertas.append([atendimento, espera])

        return merge_sort(alertas, menos_o_numero)