import csv
import os
from datetime import datetime
from modelos.atendimento import Atendimento, ESTADO_FINALIZADO
from modelos.cliente import Cliente
from persistencia.exportacao import gravar_csv, texto_de_data_hora
from servicos.servico_atendentes import ServicoAtendentes
from servicos.servico_atendimentos import ServicoAtendimentos
from servicos.servico_clientes import ServicoClientes

ARQUIVO_CLIENTES = "clientes.csv"
ARQUIVO_ATENDENTES = "atendentes.csv"
ARQUIVO_ATENDIMENTOS = "atendimentos.csv"
CABECALHO_CLIENTES = ["id", "nome", "telefone", "prioridade", "ultima_atividade"]
CABECALHO_ATENDENTES = ["id", "nome"]
CABECALHO_ATENDIMENTOS = [
    "id", "estado", "id_cliente", "nome_cliente", "telefone_cliente",
    "prioridade_cliente", "id_atendente", "hora_entrada", "hora_inicio",
    "hora_fim", "ultima_atividade_anterior",
]

def linha_do_atendimento(atendimento):
    cliente = atendimento.cliente
    id_atendente = ""
    if atendimento.atendente is not None:
        id_atendente = atendimento.atendente.id

    return [
        atendimento.id,
        atendimento.estado,
        cliente.id,
        cliente.nome,
        cliente.telefone,
        cliente.prioridade,
        id_atendente,
        texto_de_data_hora(atendimento.hora_entrada),
        texto_de_data_hora(atendimento.hora_inicio),
        texto_de_data_hora(atendimento.hora_fim),
        texto_de_data_hora(atendimento.ultima_atividade_anterior),
    ]

def salvar_sistema(pasta, servico_clientes, servico_atendentes, servico_atendimentos):
    os.makedirs(pasta, exist_ok=True)
    linhas_clientes = []
    for cliente in servico_clientes.listar():
        linhas_clientes.append([
            cliente.id,
            cliente.nome,
            cliente.telefone,
            cliente.prioridade,
            texto_de_data_hora(cliente.ultima_atividade),
        ])
    gravar_csv(os.path.join(pasta, ARQUIVO_CLIENTES), CABECALHO_CLIENTES, linhas_clientes)

    linhas_atendentes = []
    for atendente in servico_atendentes.listar():
        linhas_atendentes.append([atendente.id, atendente.nome])
    gravar_csv(os.path.join(pasta, ARQUIVO_ATENDENTES), CABECALHO_ATENDENTES, linhas_atendentes)

    todos = list(servico_atendimentos.historico)
    for atendimento in servico_atendimentos.em_andamento_por_atendente.values():
        todos.append(atendimento)
    todos = todos + servico_atendimentos.fila_comum.listar()
    todos = todos + servico_atendimentos.fila_prioridade.listar()

    linhas_atendimentos = []
    for atendimento in todos:
        linhas_atendimentos.append(linha_do_atendimento(atendimento))
    gravar_csv(
        os.path.join(pasta, ARQUIVO_ATENDIMENTOS),
        CABECALHO_ATENDIMENTOS,
        linhas_atendimentos,
    )

def data_de_texto(texto):
    if texto == "":
        return None
    return datetime.fromisoformat(texto)

def ler_linhas(caminho):
    try:
        with open(caminho, "r", newline="", encoding="utf-8") as arquivo:
            leitor = csv.reader(arquivo)
            next(leitor, None)
            return list(leitor)
    except FileNotFoundError:
        return []

def processar_arquivo(pasta, nome_arquivo, processar_linha, avisos):
    numero_linha = 1    # a linha 1 é o cabeçalho
    for linha in ler_linhas(os.path.join(pasta, nome_arquivo)):
        numero_linha = numero_linha + 1
        try:
            processar_linha(linha)
        except (ValueError, IndexError) as erro:
            avisos.append(
                nome_arquivo + ", linha " + str(numero_linha) + " ignorada: " + str(erro)
            )

def montar_atendimento(linha, servico_clientes, servico_atendentes):
    id_atendimento = int(linha[0])
    estado = linha[1]
    id_cliente = int(linha[2])
    cliente = servico_clientes.buscar(id_cliente)
    if cliente is None:
        if estado != ESTADO_FINALIZADO:
            raise ValueError("o cliente " + str(id_cliente) + " deste atendimento não existe.")
        cliente = Cliente(id_cliente, linha[3], linha[4], int(linha[5]))

    atendimento = Atendimento(id_atendimento, cliente, data_de_texto(linha[7]))
    atendimento.estado = estado
    atendimento.hora_inicio = data_de_texto(linha[8])
    atendimento.hora_fim = data_de_texto(linha[9])
    atendimento.ultima_atividade_anterior = data_de_texto(linha[10])

    if linha[6] != "":
        atendente = servico_atendentes.buscar(int(linha[6]))
        if atendente is None:
            raise ValueError("o atendente " + linha[6] + " deste atendimento não existe.")
        atendimento.atendente = atendente
    return atendimento

def carregar_sistema(pasta):
    servico_clientes = ServicoClientes()
    servico_atendentes = ServicoAtendentes()
    servico_atendimentos = ServicoAtendimentos(servico_clientes, servico_atendentes)
    avisos = []

    def carregar_cliente(linha):
        servico_clientes.cadastrar(
            int(linha[0]), linha[1], linha[2], int(linha[3]), data_de_texto(linha[4])
        )

    def carregar_atendente(linha):
        servico_atendentes.cadastrar(int(linha[0]), linha[1])

    def carregar_atendimento(linha):
        atendimento = montar_atendimento(linha, servico_clientes, servico_atendentes)
        servico_atendimentos.restaurar(atendimento)

    processar_arquivo(pasta, ARQUIVO_CLIENTES, carregar_cliente, avisos)
    processar_arquivo(pasta, ARQUIVO_ATENDENTES, carregar_atendente, avisos)
    processar_arquivo(pasta, ARQUIVO_ATENDIMENTOS, carregar_atendimento, avisos)
    return servico_clientes, servico_atendentes, servico_atendimentos, avisos