def ordenar_bublesort(vetor):
    # Cria uma copia do vetor para nao modificar a entrada original.
    arr = list(vetor)
    # Inicializa o contador de comparacoes com zero.
    comparacoes = 0
    # Captura o tamanho do vetor para controlar os limites dos lacos.
    n = len(arr)
    # Inicia o laco externo do Bubble Sort.
    for i in range(n):
        # Inicia o laco interno para mover o menor elemento para o inicio.
        for j in range(n - 1, i, -1):
            # Conta a comparacao entre elementos adjacentes.
            comparacoes += 1
            # Verifica se o elemento da direita e menor que o da esquerda.
            if arr[j] < arr[j - 1]:
                # Troca os elementos para manter a ordem crescente.
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
    # Retorna o vetor ordenado e a quantidade total de comparacoes.
    return arr, comparacoes
