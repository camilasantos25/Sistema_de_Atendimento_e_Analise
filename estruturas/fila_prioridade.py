from estruturas.fila import Fila

class FilaPrioridade:
    def __init__(self, maior_prioridade):
        self.maior_prioridade = maior_prioridade
        self.filas = []
        for nivel in range(maior_prioridade + 1):
            self.filas.append(Fila())

    def entrar(self, item, prioridade):
        if prioridade < 0 or prioridade > self.maior_prioridade:
            raise ValueError("Prioridade inválida para esta fila.")
        self.filas[prioridade].entrar(item)

    def sair(self):
        nivel = self._nivel_do_proximo()
        if nivel is None:
            raise ValueError("A fila de prioridade está vazia.")
        return self.filas[nivel].sair()

    def espiar(self):
        nivel = self._nivel_do_proximo()
        if nivel is None:
            raise ValueError("A fila de prioridade está vazia.")
        return self.filas[nivel].espiar()

    def tamanho(self):
        total = 0
        for fila in self.filas:
            total = total + fila.tamanho()
        return total

    def esta_vazia(self):
        return self._nivel_do_proximo() is None

    def listar(self):
        todos = []
        for nivel in range(self.maior_prioridade, -1, -1):
            for item in self.filas[nivel].listar():
                todos.append(item)
        return todos

    def _nivel_do_proximo(self):
        for nivel in range(self.maior_prioridade, -1, -1):
            if not self.filas[nivel].esta_vazia():
                return nivel
        return None