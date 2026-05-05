def ordenar_heap(vetor):
    # Cria uma copia do vetor para preservar a entrada original.
    arr = list(vetor)
    # Inicializa o contador total de comparacoes.
    comparacoes = 0
    # Define o tamanho inicial do heap como o tamanho do vetor.
    tamanho_heap = len(arr)

    # Define funcao MAX-HEAPIFY corrige a propriedade de heap.
    def max_heapify(i):
        # Permite alterar variaveis do escopo externo.
        nonlocal comparacoes, tamanho_heap
        # Calcula o indice do filho esquerdo.
        esquerda = 2 * i + 1
        # Calcula o indice do filho direito.
        direita = 2 * i + 2
        # Inicializa maior como o indice atual.
        maior = i
        # Verifica se o filho esquerdo existe dentro do heap.
        if esquerda < tamanho_heap:
            # Conta a comparacao entre o filho esquerdo e o elemento atual.
            comparacoes += 1
            # Atualiza maior se o filho esquerdo for maior.
            if arr[esquerda] > arr[maior]:
                # Define o filho esquerdo como maior candidato.
                maior = esquerda
        # Verifica se o filho direito existe dentro do heap.
        if direita < tamanho_heap:
            # Conta a comparacao entre o filho direito e o maior atual.
            comparacoes += 1
            # Atualiza maior se o filho direito for maior.
            if arr[direita] > arr[maior]:
                # Define o filho direito como maior candidato.
                maior = direita
        # Verifica se houve mudanca do maior elemento.
        if maior != i:
            # Troca o elemento atual com o maior filho.
            arr[i], arr[maior] = arr[maior], arr[i]
            # Continua heapificando recursivamente a subarvore afetada.
            max_heapify(maior)

    # Constrói o max-heap a partir do vetor nao ordenado.
    # divide o tamanho do vetor por 2 para obter o indice do ultimo nó interno (nós que tem filhos).
    for i in range((len(arr) // 2) - 1, -1, -1):
        # Aplica heapify em cada no interno.
        max_heapify(i)

    # Extrai repetidamente o maior elemento e reorganiza o heap.
    for i in range(len(arr) - 1, 0, -1):
        # Move a raiz (maior elemento) para a posicao final atual.
        arr[0], arr[i] = arr[i], arr[0]
        # Reduz o tamanho efetivo do heap em uma unidade.
        tamanho_heap -= 1
        # Restaura a propriedade de max-heap a partir da raiz.
        max_heapify(0)

    # Retorna o vetor ordenado e a quantidade de comparacoes.
    return arr, comparacoes
