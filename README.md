# Sistema Completo de Atendimento e Análise

Sistema de linha de comando, feito em Python, para gerenciar atendimentos de uma clínica ou central de atendimento: cadastro de clientes e atendentes, filas comum e de prioridade, histórico, desfazer finalização, remoção de clientes inativos, relatórios e exportação em CSV.

O projeto foi desenvolvido para praticar Estrutura de Dados. Cada estrutura foi implementada manualmente (sem usar versões prontas que escondam o funcionamento) e escolhida pelo custo das operações que o sistema mais executa.

## Funcionalidades

- Cadastro de clientes (ID, nome, telefone e prioridade)
- Cadastro de atendentes (ID e nome)
- Abertura de atendimento, colocando o cliente na fila certa
- Fila comum e fila de prioridade
- Chamada do próximo cliente, respeitando prioridade e ordem de chegada
- Finalização de atendimento (data, duração, atendente e cliente)
- Histórico de atendimentos de cada cliente
- Desfazer a última finalização (usando uma pilha)
- Remoção de clientes inativos (usando uma lista encadeada)
- Busca de cliente por ID (busca binária em vetor ordenado)
- Relatório de tempo médio de atendimento
- Relatório dos cinco clientes mais atendidos
- Filtro de atendimentos por data
- Alertas de tempo de espera elevado
- Exportação dos relatórios em CSV
- Persistência dos dados em arquivos CSV
- Logs das operações importantes

## Regras de negócio

- Clientes prioritários são atendidos antes dos comuns.
- Clientes com a mesma prioridade mantêm a ordem de chegada.
- Cada atendente só atende um cliente por vez.
- Não é possível finalizar um atendimento sem que exista um em andamento.
- Não é possível remover um cliente com atendimento aberto (aguardando ou em andamento).
- IDs de clientes e de atendentes são únicos.
- Os dados são validados (ID maior que zero, nome não vazio, telefone com 10 ou 11 dígitos, prioridade válida).
- Desfazer uma finalização restaura o estado anterior: o atendimento volta a "em andamento", sai do histórico, o atendente volta a ficar ocupado e o cliente recupera a data da última atividade anterior.

### Decisões tomadas onde o enunciado não definia

- **Prioridade:** número inteiro. `0` é comum, `1` é preferencial e `2` é urgente. O `0` vai para a fila comum, e o `1` e o `2` para a fila de prioridade, onde o `2` passa na frente do `1`.
- **Um atendimento aberto por cliente:** um cliente não pode estar duas vezes nas filas nem ser atendido por dois atendentes ao mesmo tempo.
- **Fila de prioridade sempre vence a comum.** Para evitar que um cliente comum espere sem limite, existe o alerta de espera elevada.
- **Cliente inativo:** não tem atendimento aberto e sua última atividade (cadastro ou finalização de atendimento) foi há mais de N dias, com N escolhido por quem usa.
- **Remover um cliente não apaga o histórico dele.** Os relatórios continuam contando os atendimentos já finalizados.
- **Desfazer é recusado** se o atendente já atende outro cliente, se o cliente abriu outro atendimento ou se o cliente foi removido.
- **Data de um atendimento nos filtros:** a data em que ele começou.
- **Empate no ranking dos mais atendidos:** o menor ID vem primeiro.
- **Espera igual ao limite não gera alerta:** só quem espera mais que o limite.

## Requisitos

- Python 3.10 ou superior (desenvolvido com Python 3.14)
- Nenhuma biblioteca externa

## Tecnologias

Somente a biblioteca padrão do Python: `csv`, `datetime`, `logging`, `os`, `unittest`, `tempfile`.

## Organização dos módulos

O código é dividido em camadas, e cada uma só conhece as de baixo:

```
interface  →  persistencia  →  servicos  →  modelos / estruturas
```

```
sistema-atendimento-analise/
├── main.py                      # ponto de entrada: liga os logs e abre o menu
├── estruturas/                  # estruturas de dados (não sabem o que é um cliente)
│   ├── vetor_ordenado.py        # vetor ordenado por ID + busca binária
│   ├── lista_encadeada.py       # nós, cabeça, cauda, remoção em lote
│   ├── fila.py                  # fila comum (FIFO)
│   ├── fila_prioridade.py       # uma fila por nível de prioridade
│   ├── pilha.py                 # pilha (LIFO) do "desfazer"
│   └── ordenacao.py             # insertion sort, merge sort (recursivo) e intercalar
├── modelos/                     # os dados e suas validações
│   ├── validacoes.py            # validações comuns (ID e nome)
│   ├── cliente.py
│   ├── atendente.py
│   └── atendimento.py
├── servicos/                    # regras de negócio
│   ├── servico_clientes.py
│   ├── servico_atendentes.py
│   ├── servico_atendimentos.py  # abrir, chamar, finalizar, desfazer, inativos
│   ├── servico_relatorios.py
│   └── registro.py              # configuração dos logs
├── persistencia/                # leitura e escrita de arquivos
│   ├── armazenamento.py         # salvar e reconstruir o sistema
│   └── exportacao.py            # exportação dos relatórios
├── interface/                   # terminal (único lugar com print e input)
│   ├── entrada.py               # leitura e validação do que o usuário digita
│   ├── apresentacao.py          # formatação de textos
│   ├── sistema.py               # junta serviços e persistência
│   └── menu.py                  # as opções do menu
├── testes/                      # testes unitários
├── dados/                       # criada automaticamente ao salvar
└── logs/                        # criada automaticamente ao abrir o sistema
```

**Por que separar assim:**

- **Estruturas:** não conhecem clientes. O mesmo `VetorOrdenado` guarda clientes e atendentes, e a `Fila` guarda atendimentos.
- **Modelos:** validam os próprios dados. Um objeto inválido nunca chega a existir.
- **Serviços:** coordenam estruturas e modelos e aplicam as regras. Nunca usam `print` ou `input`.
- **Persistência:** só lê e escreve arquivos. Os serviços nunca dependem dela.
- **Interface:** só conversa com o usuário e chama os serviços.

Isso permite testar as regras sem digitar nada no terminal, e trocar o terminal por outra interface mexendo só em `interface/`.

## Como executar

Na pasta raiz do projeto:

```
python main.py
```

Os dados são carregados da pasta `dados/` ao abrir e gravados na opção `0` (Salvar e sair) ou na `19` (Salvar agora). Na primeira execução o sistema começa vazio.

**Atenção:** se o programa for fechado de outra forma (`Ctrl+C` ou fechando a janela), as alterações desde o último salvamento são perdidas.

## Como executar os testes

Na pasta raiz do projeto:

```
python -m unittest -v
```

São 229 testes, que cobrem as estruturas, as regras de negócio, a persistência, a exportação, os logs e o menu. Os testes que gravam arquivos usam pastas temporárias e não deixam resíduos.

## Exemplo de utilização

```
===== Sistema de Atendimento e Análise =====
1 - Cadastrar cliente
2 - Buscar cliente por ID
3 - Listar clientes
4 - Remover cliente
5 - Remover clientes inativos
6 - Cadastrar atendente
7 - Listar atendentes
8 - Abrir atendimento (entrar na fila)
9 - Chamar próximo cliente
10 - Finalizar atendimento
11 - Desfazer última finalização
12 - Ver filas e atendimentos em andamento
13 - Histórico de atendimentos de um cliente
14 - Tempo médio de atendimento
15 - Cinco clientes mais atendidos
16 - Atendimentos por data
17 - Alertas de espera elevada
18 - Exportar relatórios em CSV
19 - Salvar agora
0 - Salvar e sair
Escolha: 1
ID do cliente: 1
Nome: Ana
Telefone (só números, com DDD): 11999990000
Prioridade (0 comum, 1 preferencial, 2 urgente): 0
Cliente cadastrado!
Escolha: 6
ID do atendente: 1
Nome: Carla
Atendente cadastrado!
Escolha: 8
ID do cliente: 1
Atendimento 1 aberto: Ana entrou na fila (comum).
Escolha: 9
ID do atendente: 1
Atendente Carla chama: Ana (atendimento 1, comum).
Escolha: 10
ID do atendente: 1
Atendimento 1 finalizado. Duração: 4 min 12 s.
Escolha: 14
Tempo médio de atendimento: 4 min 12 s (1 atendimento(s)).
```

Entradas inválidas não derrubam o programa: a pergunta é repetida com uma mensagem, e operações recusadas pelas regras de negócio mostram o motivo e voltam ao menu.

## Persistência

Os dados ficam em três arquivos CSV na pasta `dados/`:

| Arquivo | Conteúdo |
|---|---|
| `clientes.csv` | ID, nome, telefone, prioridade e data da última atividade |
| `atendentes.csv` | ID e nome |
| `atendimentos.csv` | todos os atendimentos, em qualquer estado, com IDs, estado e horas |

O princípio é **salvar dados, e não referências**. Um objeto que aponta para outro (um atendimento que aponta para um cliente) vira o ID do outro no arquivo, e as ligações são refeitas ao carregar, procurando cada ID no cadastro. As estruturas em si nunca são gravadas, elas são reconstruídas:

- **Vetor ordenado e lista encadeada de ativos:** refeitos pelo cadastro de cada cliente.
- **Filas:** os atendimentos "aguardando" são gravados na ordem em que seriam chamados e recolocados na fila nessa ordem.
- **Pilha do desfazer:** o histórico é gravado em ordem, e cada atendimento finalizado é empilhado ao ser lido. A pilha tem sempre os mesmos itens do histórico, na mesma ordem.
- **O atendente "ocupado":** não é gravado, é recalculado a partir dos atendimentos em andamento.
- **Próximo ID de atendimento:** o maior ID existente mais 1.
- **Cliente removido que ainda tem histórico:** o `atendimentos.csv` guarda uma "foto" (nome, telefone e prioridade) do cliente, para o histórico continuar completo.

Linhas inválidas ou incoerentes nos arquivos são ignoradas e viram avisos com o arquivo e o número da linha. As linhas válidas continuam sendo carregadas.

## Exportação de relatórios

A opção `18` grava quatro arquivos CSV em `dados/relatorios/`:

| Arquivo | Conteúdo |
|---|---|
| `tempo_medio.csv` | total de atendimentos e tempo médio em segundos |
| `top_clientes.csv` | ranking dos cinco clientes mais atendidos |
| `atendimentos.csv` | histórico de atendimentos finalizados, com datas e durações |
| `alertas_de_espera.csv` | clientes esperando mais que o limite informado |

Datas saem no formato ISO (`2026-10-01T10:00:00`) e durações em segundos, para facilitar o uso em planilhas.

## Logs

O arquivo `logs/sistema.log` registra uma linha por operação importante, sempre com **IDs** e nunca com nomes ou telefones:

```
2026-11-01 20:05:11,123 | INFO | Atendimento 1 aberto: cliente 1, prioridade 0
2026-11-01 20:05:40,456 | INFO | Atendimento 1 chamado: atendente 1 atende o cliente 1
2026-11-01 20:09:52,789 | INFO | Atendimento 1 finalizado: atendente 1, cliente 1, duração 252.0 segundos
```

São registrados: abertura, chamada, finalização e desfazimento de atendimentos, cadastros, remoções, salvamento e carregamento. Operações recusadas viram `WARNING`, e falhas de arquivo viram `ERROR`. Os logs de uma execução se acumulam depois dos anteriores.

## Estruturas de dados utilizadas

### Vetor ordenado (clientes e atendentes)

Uma lista Python que nunca sai de ordem crescente de ID. Cada inserção encontra a posição correta e empurra os itens seguintes. Serve à **busca binária**, que olha o item do meio e descarta metade da lista a cada passo. Só funciona porque a lista está ordenada.

- **Vantagem:** busca por ID em O(log n).
- **Limitação:** inserir e remover custam O(n), por causa do deslocamento.
- **Por que foi escolhido:** a busca por ID é a operação mais frequente (toda abertura e chamada de atendimento busca um cliente ou atendente), e o cadastro acontece bem menos.

### Vetor não ordenado (histórico de atendimentos)

O histórico é uma lista Python em que cada atendimento finalizado é acrescentado no fim, na ordem em que terminou. Não há ordem por nenhuma chave de busca.

- **Vantagem:** acrescentar no fim é O(1).
- **Limitação:** qualquer consulta (por cliente, por data) percorre a lista, em O(n).
- **Por que foi escolhido:** o histórico é escrito a cada finalização e lido só nos relatórios. O custo de manter outra ordem não compensaria.

### Fila comum (FIFO)

Uma lista com um marcador de início. Entrar é acrescentar no fim, e sair é avançar o marcador, sem deslocar ninguém. Quando o espaço já usado passa da metade da lista, ela é limpa, o que mantém o custo médio de sair em O(1) (amortizado).

- **Por que não `pop(0)`:** remover do começo de uma lista desloca todos os itens, custando O(n).

### Fila de prioridade

Uma lista de filas comuns, uma por nível de prioridade, em que a posição na lista é o próprio nível. Entrar coloca o item na fila do nível dele, e sair olha do nível mais alto para o mais baixo e tira da primeira fila que não está vazia.

- **A ordem de chegada dentro de cada nível vem de graça**, porque cada nível é uma fila FIFO.
- **Custo:** O(1), pois o número de níveis é fixo e pequeno (3).
- **Limitação:** serve para poucos níveis fixos. Para prioridades arbitrárias, a alternativa é um heap, que usa árvores.
- **Alternativas consideradas:** lista ordenada na inserção (entrar custaria O(n)) e lista não ordenada (sair custaria O(n)).

### Pilha (LIFO)

Uma lista em que só se entra e se sai pelo fim. Cada finalização é empilhada, e desfazer tira a do topo. Como a pilha guarda o próprio objeto do atendimento, que já contém cliente, atendente e horas, tudo que a finalização alterou pode ser revertido.

### Lista encadeada (clientes ativos)

Nós ligados por referências, com uma `cabeca` (primeiro nó) e uma `cauda` (último nó). Cada nó guarda um dado e uma referência para o próximo. Inserir no fim e no início não desloca nada. O método `remover_se` percorre a lista uma única vez e desliga todos os nós que satisfazem uma condição, o que é usado para remover clientes inativos.

- **Vantagem:** desligar um nó é só trocar uma referência, sem deslocar itens.
- **Limitação:** não permite busca binária (não há acesso direto ao meio), então buscar custa O(n).
- **Por isso o sistema usa as duas:** o vetor ordenado para buscar por ID, e a lista encadeada para a remoção em lote. Os dois guardam os mesmos objetos e são mantidos em sincronia.

### Dicionários

Dois dicionários auxiliares associam cliente → atendimento aberto e atendente → atendimento em andamento. Servem para consultar em O(1), em média, se um cliente já tem atendimento aberto ou se um atendente está ocupado.

## Algoritmos

### Busca binária

Usada para buscar clientes e atendentes por ID. O(log n).

### Insertion sort

Encaixa um item por vez na parte já ordenada, empurrando os maiores. Estável, e rápido em listas quase ordenadas. É usado no filtro de atendimentos por data, porque o histórico já está quase na ordem de início.

### Merge sort (recursivo)

Divide a lista ao meio, ordena cada metade chamando a si mesmo e junta as duas metades ordenadas (`intercalar`). É a rotina recursiva do sistema:

- **Caso-base:** lista com 0 ou 1 item, que já está ordenada.
- **Caso recursivo:** ordenar a primeira metade e a segunda metade.
- **Profundidade da recursão:** O(log n), então não há risco de estourar o limite de chamadas do Python.
- É usado no ranking dos mais atendidos e nos alertas de espera.
- **Estável:** no empate, mantém a ordem original. Isso é usado para ordenar o ranking duas vezes (primeiro por ID, depois pelo total), garantindo o desempate pelo menor ID.

As funções `sorted()` e `list.sort()` do Python **não** são usadas no sistema. Aparecem apenas nos testes, como gabarito para conferir o resultado dos algoritmos implementados.

## Complexidade das operações

Considere `n` clientes, `m` atendentes, `h` atendimentos no histórico, `c` clientes diferentes no histórico, `k` itens do resultado de uma operação e `w` clientes em espera.

| Operação | Estrutura | Custo | Justificativa |
|---|---|---|---|
| Buscar cliente por ID | vetor ordenado | O(log n) | busca binária descarta metade a cada passo |
| Cadastrar cliente | vetor ordenado + lista encadeada | O(n) | achar a posição e deslocar itens domina; a lista é O(1) no fim |
| Remover cliente | vetor ordenado + lista encadeada | O(n) | busca O(log n), mas a remoção nas duas estruturas é O(n) |
| Remover inativos | lista encadeada | O(n + k·n) | uma passada na lista, mais a remoção de cada um dos k clientes no vetor |
| Abrir atendimento | busca binária + fila | O(log n) | achar o cliente; entrar na fila é O(1) |
| Entrar na fila comum | fila | O(1) | só acrescenta no fim |
| Sair da fila comum | fila | O(1) amortizado | avança um marcador; a limpeza é rara |
| Entrar e sair da fila de prioridade | lista de filas | O(1) | número fixo de níveis |
| Chamar próximo | busca binária + filas | O(log m) | achar o atendente; sair das filas é O(1) |
| Finalizar atendimento | dicionários + pilha | O(1) | sem percorrer nada |
| Desfazer finalização | pilha + busca binária | O(log n) | `topo` e `desempilhar` são O(1); confere o cliente por busca binária |
| Histórico de um cliente | vetor não ordenado | O(h) | percorre o histórico |
| Tempo médio | vetor não ordenado | O(h) | uma passada, somando as durações |
| Cinco mais atendidos | dicionário + merge sort | O(h + c log c) | contagem e duas ordenações O(c log c) |
| Atendimentos por data | vetor não ordenado + insertion sort | O(h + k²) pior caso, O(h + k) quase ordenado | filtra em O(h); o insertion sort é O(k²) no pior caso |
| Alertas de espera | filas + merge sort | O(w log w) | listar as filas e ordenar os alertas |
| Insertion sort | | O(n²) pior, O(n) melhor | dois laços aninhados; melhor caso já ordenado. Memória do algoritmo O(1) |
| Merge sort | | O(n log n) | log n níveis de divisão, O(n) de trabalho por nível. Memória O(n) |
| Salvar sistema | CSV | O(n + m + h) | uma linha por registro |
| Carregar sistema | CSV | O(n² + m² + h) | cada cadastro é O(n) por causa da inserção ordenada |
| Exportar relatório | CSV | O(k) | uma linha por registro |
| Registrar uma linha de log | arquivo | O(1) | acrescenta uma linha no fim |

**Custo teórico não é tempo real.** O Big-O mede como o trabalho cresce com o tamanho dos dados. Com poucos clientes, tudo roda instantaneamente. Operações com disco (salvar, exportar, logs) são muito mais lentas que operações em memória, mesmo quando têm a mesma notação.

## Limitações

- Os dados só são gravados ao salvar. Fechar o programa de outra forma perde as alterações desde o último salvamento.
- A gravação dos CSVs não é à prova de queda de energia no meio do salvamento.
- A fila de prioridade funciona para poucos níveis fixos de prioridade.
- O carregamento custa O(n²) por causa da inserção ordenada, o que é irrelevante para o tamanho previsto do sistema.
- A lista encadeada de ativos é refeita em ordem de ID ao carregar, e não na ordem original de cadastro.
- A remoção de clientes inativos custa O(n²) no pior caso, quando todos saem.
- O relatório de atendimentos considera apenas atendimentos finalizados.
- Não há confirmação antes de remover clientes.
