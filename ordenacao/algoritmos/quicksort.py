import random

def ordenar_quicksort(vetor):
    # Cria uma copia do vetor para nao alterar a entrada fornecida.
    arr = list(vetor)
    # Inicializa o contador de comparacoes com zero.
    comparacoes = 0

    # Define funcao PARTITION.
    def particionar(p, r):
        # Permite escrita no contador do escopo externo.
        nonlocal comparacoes
        # Escolhe pivô aleatório e troca com o final
        pivot_index = random.randint(p, r)
        arr[pivot_index], arr[r] = arr[r], arr[pivot_index]
        pivo = arr[r]
        # Inicializa i para delimitar a regiao de elementos menores ou iguais ao pivo.
        i = p - 1
        # Percorre os elementos do segmento, exceto o pivo.
        for j in range(p, r):
            # Conta a comparacao entre elemento atual e pivo.
            comparacoes += 1
            # Verifica se o elemento atual deve ficar na particao da esquerda.
            if arr[j] <= pivo:
                # Avanca o limite da particao esquerda.
                i += 1
                # Troca o elemento atual para a regiao correta.
                arr[i], arr[j] = arr[j], arr[i]
        # Coloca o pivo entre as duas particoes.
        arr[i + 1], arr[r] = arr[r], arr[i + 1]
        # Retorna o indice final do pivo.
        return i + 1

    # Define funcao recursiva QUICKSORT.
    def quicksort(p, r):
        # Verifica condicao de parada do segmento.
        if p < r:
            # Particiona o segmento e obtem a posicao final do pivo.
            q = particionar(p, r)
            # Ordena recursivamente a particao da esquerda.
            quicksort(p, q - 1)
            # Ordena recursivamente a particao da direita.
            quicksort(q + 1, r)

    # Executa o quicksort quando ha elementos no vetor.
    if arr:
        # Chama quicksort para todo o intervalo do vetor.
        quicksort(0, len(arr) - 1)
    # Retorna o vetor ordenado e a quantidade total de comparacoes.
    return arr, comparacoes
