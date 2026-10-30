def validar_id(id_pessoa):
    if id_pessoa <= 0:
        raise ValueError("O ID deve ser maior que zero.")

def validar_nome(nome):
    if nome.strip() == "":
        raise ValueError("O nome não pode ficar vazio.")