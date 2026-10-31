class No:
    def __init__(self, dado):
        self.dado = dado
        self.proximo = None

class ListaEncadeada:
    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self.quantidade = 0

    def esta_vazia(self):
        return self.cabeca is None

    def tamanho(self):
        return self.quantidade

    def inserir_no_inicio(self, dado):
        no = No(dado)
        no.proximo = self.cabeca
        self.cabeca = no
        if self.cauda is None:
            self.cauda = no
        self.quantidade = self.quantidade + 1

    def inserir_no_fim(self, dado):
        no = No(dado)
        if self.cabeca is None:
            self.cabeca = no
            self.cauda = no
        else:
            self.cauda.proximo = no
            self.cauda = no
        self.quantidade = self.quantidade + 1

    def buscar(self, id_item):
        atual = self.cabeca
        while atual is not None:
            if atual.dado.id == id_item:
                return atual.dado
            atual = atual.proximo
        return None

    def remover(self, id_item):
        anterior = None
        atual = self.cabeca
        while atual is not None:
            if atual.dado.id == id_item:
                if anterior is None:
                    self.cabeca = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                if atual is self.cauda:
                    self.cauda = anterior
                self.quantidade = self.quantidade - 1
                return atual.dado
            anterior = atual
            atual = atual.proximo
        return None

    def remover_se(self, condicao):
        removidos = []
        anterior = None
        atual = self.cabeca
        while atual is not None:
            proximo = atual.proximo
            if condicao(atual.dado):
                if anterior is None:
                    self.cabeca = proximo
                else:
                    anterior.proximo = proximo
                if atual is self.cauda:
                    self.cauda = anterior
                self.quantidade = self.quantidade - 1
                removidos.append(atual.dado)
            else:
                anterior = atual
            atual = proximo
        return removidos

    def listar(self):
        resultado = []
        atual = self.cabeca
        while atual is not None:
            resultado.append(atual.dado)
            atual = atual.proximo
        return resultado