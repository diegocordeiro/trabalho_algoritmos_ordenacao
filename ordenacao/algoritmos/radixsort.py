def ordenar_radixsort(vetor):
    """
    LSD Radix Sort com base 65536 (16 bits por digito).

    Algoritmo de ordenacao nao-comparativo que processa os elementos
    digito a digito (do menos significativo para o mais significativo),
    utilizando Counting Sort como sub-rotina estavel em cada passada.

    Complexidade: O(d * n) onde d = numero de digitos (passadas).
    Com base 65536:
      - N ate 65.535   -> 1 passada
      - N ate ~4.3 Bi  -> 2 passadas
    Para todos os tamanhos testados no benchmark (ate 200K),
    sao necessarias no maximo 2 passadas.

    Espaco adicional: O(n + 65536) = O(n)

    Retorna (vetor_ordenado, comparacoes).
    Como o algoritmo e nao-comparativo, o contador de comparacoes
    sera sempre 0.
    """
    arr = list(vetor)
    n = len(arr)

    if n <= 1:
        return arr, 0

    # Base 65536 = 2^16 (16 bits por digito)
    BASE = 65536
    MASCARA = BASE - 1  # 0xFFFF

    # Determina o valor maximo para saber quantas passadas sao necessarias
    max_val = arr[0]
    for i in range(1, n):
        if arr[i] > max_val:
            max_val = arr[i]

    # Array auxiliar para a ordenacao estavel em cada passada
    saida = [0] * n

    # Processa cada grupo de 16 bits (do menos significativo para o mais)
    deslocamento = 0
    while max_val >> deslocamento > 0:
        # Array de contagem para a base atual
        contagem = [0] * BASE

        # Conta a frequencia de cada digito
        for valor in arr:
            digito = (valor >> deslocamento) & MASCARA
            contagem[digito] += 1

        # Soma prefixada para determinar as posicoes finais
        for i in range(1, BASE):
            contagem[i] += contagem[i - 1]

        # Posiciona os elementos de forma estavel (da direita para a esquerda)
        for i in range(n - 1, -1, -1):
            valor = arr[i]
            digito = (valor >> deslocamento) & MASCARA
            contagem[digito] -= 1
            saida[contagem[digito]] = valor

        # Copia de volta para o array principal
        arr, saida = saida, arr

        # Avanca para o proximo grupo de 16 bits
        deslocamento += 16

    # Radix Sort e nao-comparativo, portanto 0 comparacoes
    return arr, 0