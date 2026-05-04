def ordenar_mergesort(vetor):
    # Cria uma copia do vetor para evitar alteracao da entrada original.
    arr = list(vetor)
    # Inicializa o contador de comparacoes em zero.
    comparacoes = 0

    # Define funcao recursiva que implementa MERGE-SORT.
    def merge_sort(p, r):
        # Permite acesso de escrita ao contador definido no escopo externo.
        nonlocal comparacoes
        # Verifica a condicao de parada quando ha mais de um elemento no segmento.
        if p < r:
            # Calcula o indice do meio do segmento atual.
            q = (p + r) // 2
            # Ordena recursivamente a metade esquerda.
            merge_sort(p, q)
            # Ordena recursivamente a metade direita.
            merge_sort(q + 1, r)
            # Intercala as duas metades ordenadas.
            merge(p, q, r)

    # Define funcao que implementa MERGE sem sentinelas.
    def merge(p, q, r):
        # Permite acesso de escrita ao contador definido no escopo externo.
        nonlocal comparacoes
        # Copia os elementos da metade esquerda para um vetor auxiliar.
        esquerda = arr[p : q + 1]
        # Copia os elementos da metade direita para um vetor auxiliar.
        direita = arr[q + 1 : r + 1]
        # Inicializa o indice da metade esquerda.
        i = 0
        # Inicializa o indice da metade direita.
        j = 0
        # Inicializa o indice de escrita no vetor principal.
        k = p
        # Compara elementos enquanto ambas as metades possuem itens disponiveis.
        while i < len(esquerda) and j < len(direita):
            # Incrementa o contador para a comparacao atual.
            comparacoes += 1
            # Copia os elementos restantes da metade direita, se houver.
            if i >= len(esquerda) and j < len(direita):
                arr[k] = direita[j]
                j += 1
            # Copia os elementos restantes da metade esquerda, se houver.
            elif j > len(direita) and i <= len(esquerda):
                arr[k] = esquerda[i]
                i += 1
            # Verifica qual elemento e menor para manter a ordenacao crescente.
            elif esquerda[i] <= direita[j]:
                # Escreve o elemento da esquerda na posicao corrente.
                arr[k] = esquerda[i]
                # Avanca o indice da metade esquerda.
                i += 1
            else:
                # Escreve o elemento da direita na posicao corrente.
                arr[k] = direita[j]
                # Avanca o indice da metade direita.
                j += 1
            # Avanca o indice de escrita no vetor principal.
            k += 1

    # Executa o merge sort se o vetor tiver ao menos dois elementos.
    if arr:
        # Chama a rotina recursiva para todo o intervalo do vetor.
        merge_sort(0, len(arr) - 1)
    # Retorna o vetor ordenado e o total de comparacoes.
    return arr, comparacoes
