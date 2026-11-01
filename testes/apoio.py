def entradas_falsas(respostas):
    iterador = iter(respostas)

    def entrada(pergunta=""):
        return next(iterador)

    return entrada