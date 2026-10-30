class VetorOrdenado:
    def __init__(self):
        self.itens = []

    def _indice_de(self, id_item):
        baixo = 0
        alto = len(self.itens) - 1

        while baixo <= alto:
            meio = (baixo + alto) // 2
            id_do_meio = self.itens[meio].id

            if id_do_meio == id_item:
                return meio
            elif id_do_meio < id_item:
                baixo = meio + 1
            else:
                alto = meio - 1

        return None

    def _posicao_para_inserir(self, id_item):
        for i in range(len(self.itens)):
            if self.itens[i].id > id_item:
                return i
        return len(self.itens)

    def inserir(self, item):
        if self._indice_de(item.id) is not None:
            raise ValueError("Já existe um item com o ID " + str(item.id) + ".")

        posicao = self._posicao_para_inserir(item.id)
        self.itens.insert(posicao, item)

    def buscar(self, id_item):
        indice = self._indice_de(id_item)
        if indice is None:
            return None
        return self.itens[indice]

    def remover(self, id_item):
        indice = self._indice_de(id_item)
        if indice is None:
            return None
        return self.itens.pop(indice)

    def listar(self):
        return list(self.itens)

    def tamanho(self):
        return len(self.itens)