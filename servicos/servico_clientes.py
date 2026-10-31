from estruturas.vetor_ordenado import VetorOrdenado
from estruturas.lista_encadeada import ListaEncadeada
from modelos.cliente import Cliente

class ServicoClientes:
    def __init__(self):
        self.vetor = VetorOrdenado()
        self.ativos = ListaEncadeada()

    def cadastrar(self, id_cliente, nome, telefone, prioridade, agora=None):
        cliente = Cliente(id_cliente, nome, telefone, prioridade, agora)

        if self.vetor.buscar(cliente.id) is not None:
            raise ValueError("Já existe um cliente com o ID " + str(cliente.id) + ".")

        self.vetor.inserir(cliente)
        self.ativos.inserir_no_fim(cliente)
        return cliente

    def buscar(self, id_cliente):
        return self.vetor.buscar(id_cliente)

    def listar(self):
        return self.vetor.listar()

    def total(self):
        return self.vetor.tamanho()

    def total_ativos(self):
        return self.ativos.tamanho()

    def remover(self, id_cliente):
        cliente = self.vetor.remover(id_cliente)
        if cliente is None:
            return None
        self.ativos.remover(id_cliente)
        return cliente

    def remover_se(self, condicao):
        removidos = self.ativos.remover_se(condicao)
        for cliente in removidos:
            self.vetor.remover(cliente.id)
        return removidos