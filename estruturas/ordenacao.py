def identidade(valor):
    return valor

def insertion_sort(lista, chave=identidade):
    resultado = list(lista)

    for i in range(1, len(resultado)):
        valor = resultado[i]
        j = i - 1

        while j >= 0 and chave(resultado[j]) > chave(valor):
            resultado[j + 1] = resultado[j]
            j = j - 1

        resultado[j + 1] = valor
    return resultado

def intercalar(esquerda, direita, chave=identidade):
    resultado = []
    i = 0
    j = 0

    while i < len(esquerda) and j < len(direita):
        if chave(direita[j]) < chave(esquerda[i]):
            resultado.append(direita[j])
            j = j + 1
        else:
            resultado.append(esquerda[i])
            i = i + 1

    while i < len(esquerda):
        resultado.append(esquerda[i])
        i = i + 1
    while j < len(direita):
        resultado.append(direita[j])
        j = j + 1

    return resultado

def merge_sort(lista, chave=identidade):
    if len(lista) <= 1:
        return list(lista)

    meio = len(lista) // 2
    esquerda = merge_sort(lista[:meio], chave)
    direita = merge_sort(lista[meio:], chave)
    return intercalar(esquerda, direita, chave)