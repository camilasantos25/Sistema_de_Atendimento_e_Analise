from datetime import datetime

def converter_inteiro(texto):
    try:
        return int(texto.strip())
    except ValueError:
        raise ValueError("Digite um número inteiro.")

def converter_texto(texto):
    return texto.strip()

def converter_data(texto):
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("Digite a data no formato DD/MM/AAAA, por exemplo 25/10/2026.")

def validar_nao_negativo(valor):
    if valor < 0:
        raise ValueError("O valor não pode ser negativo.")

def ler_valor(pergunta, converter, validar=None, entrada=input, saida=print):
    while True:
        texto = entrada(pergunta)
        try:
            valor = converter(texto)
            if validar is not None:
                validar(valor)
            return valor
        except ValueError as erro:
            saida("Entrada inválida: " + str(erro))