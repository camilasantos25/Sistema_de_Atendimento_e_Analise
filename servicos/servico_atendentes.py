from estruturas.vetor_ordenado import VetorOrdenado
from modelos.atendente import Atendente

class ServicoAtendentes:
    def __init__(self):
        self.vetor = VetorOrdenado()

    def cadastrar(self, id_atendente, nome):
        atendente = Atendente(id_atendente, nome)

        if self.vetor.buscar(atendente.id) is not None:
            raise ValueError("Já existe um atendente com o ID " + str(atendente.id) + ".")

        self.vetor.inserir(atendente)
        return atendente

    def buscar(self, id_atendente):
        return self.vetor.buscar(id_atendente)

    def listar(self):
        return self.vetor.listar()

    def total(self):
        return self.vetor.tamanho()