def ordenar_countingsort(vetor):
    """
    Counting Sort - algoritmo de ordenacao nao-comparativo que agrupa
    valores iguais usando um array de contagem.

    Complexidade: O(n + k) onde k = max - min + 1
    Espaco adicional: O(k)

    Retorna (vetor_ordenado, comparacoes).
    Como o algoritmo nao realiza comparacoes entre elementos,
    o contador de comparacoes sera sempre 0.
    """
    arr = list(vetor)
    n = len(arr)

    if n <= 1:
        return arr, 0

    # Encontra o valor minimo e maximo para dimensionar o array de contagem
    minimo = arr[0]
    maximo = arr[0]
    for i in range(1, n):
        if arr[i] < minimo:
            minimo = arr[i]
        if arr[i] > maximo:
            maximo = arr[i]

    # Intervalo de valores possiveis
    intervalo = maximo - minimo + 1

    # Array de contagem inicializado com zeros
    contagem = [0] * intervalo

    # Conta a frequencia de cada valor
    for valor in arr:
        contagem[valor - minimo] += 1

    # Reconstroi o vetor ordenado agrupando valores iguais
    indice = 0
    for i in range(intervalo):
        while contagem[i] > 0:
            arr[indice] = i + minimo
            indice += 1
            contagem[i] -= 1

    # Counting Sort e nao-comparativo, portanto 0 comparacoes
    return arr, 0