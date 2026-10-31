class Fila:
    LIMITE_PARA_LIMPAR = 32

    def __init__(self):
        self.itens = []
        self.inicio = 0

    def entrar(self, item):
        self.itens.append(item)

    def sair(self):
        if self.esta_vazia():
            raise ValueError("A fila está vazia.")

        item = self.itens[self.inicio]
        self.inicio = self.inicio + 1
        self._limpar_se_preciso()
        return item

    def espiar(self):
        if self.esta_vazia():
            raise ValueError("A fila está vazia.")
        return self.itens[self.inicio]

    def tamanho(self):
        return len(self.itens) - self.inicio

    def esta_vazia(self):
        return self.tamanho() == 0

    def listar(self):
        return self.itens[self.inicio:]

    def _limpar_se_preciso(self):
        muito_lixo = self.inicio * 2 >= len(self.itens)
        if self.inicio >= self.LIMITE_PARA_LIMPAR and muito_lixo:
            self.itens = self.itens[self.inicio:]
            self.inicio = 0