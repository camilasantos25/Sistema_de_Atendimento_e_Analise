from servicos.servico_clientes import ServicoClientes

def tentar_cadastrar(servico, id_cliente, nome, telefone, prioridade):
    try:
        cliente = servico.cadastrar(id_cliente, nome, telefone, prioridade)
        print("Cadastrado:", cliente.id, cliente.nome)
    except ValueError as erro:
        print("Erro:", erro)

def mostrar_ids(servico):
    ids = []
    for cliente in servico.listar():
        ids.append(cliente.id)
    print("IDs:", ids)

servico = ServicoClientes()
print("Total inicial:", servico.total())

tentar_cadastrar(servico, 8, "Ana", "11999990000", 2)
tentar_cadastrar(servico, 3, "Davi", "11966665555", 0)
tentar_cadastrar(servico, 21, "Beatriz", "1133334444", 1)
tentar_cadastrar(servico, 8, "Outra Ana", "11900001111", 0)
tentar_cadastrar(servico, 5, "Eva", "abc", 0)

print("Total:", servico.total())
mostrar_ids(servico)
print("Busca 21:", servico.buscar(21).nome)
print("Busca 99:", servico.buscar(99))