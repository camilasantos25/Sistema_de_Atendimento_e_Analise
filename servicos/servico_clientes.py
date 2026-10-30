from estruturas.vetor_ordenado import VetorOrdenado
from modelos.cliente import Cliente

class ServicoClientes:
    def __init__(self):
        self.vetor = VetorOrdenado()

    def cadastrar(self, id_cliente, nome, telefone, prioridade):
        cliente = Cliente(id_cliente, nome, telefone, prioridade)

        if self.vetor.buscar(cliente.id) is not None:
            raise ValueError("Já existe um cliente com o ID " + str(cliente.id) + ".")

        self.vetor.inserir(cliente)
        return cliente

    def buscar(self, id_cliente):
        return self.vetor.buscar(id_cliente)

    def listar(self):
        return self.vetor.listar()

    def total(self):
        return self.vetor.tamanho()