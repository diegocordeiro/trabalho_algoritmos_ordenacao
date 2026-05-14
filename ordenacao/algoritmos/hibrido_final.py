import math
from .countingsort import ordenar_countingsort
from .insertionsort import ordenar_insertionsort
from .quicksort import ordenar_quicksort


def ordenar_hibrido_final(vetor, permitir_repetidos=False):
    """
    Algoritmo Hibrido de Ordenacao (AOH) - Versao Final.

    Estrategia:
      1. Varredura O(n) para diagnostico: verifica se o vetor ja esta
         ordenado crescentemente, conta comparacoes da varredura e,
         quando ha elementos repetidos, coleta min/max para decidir
         sobre o uso do Counting Sort.
      2. Se o vetor ja estiver crescente, retorna imediatamente com
         o numero de comparacoes da varredura.
      3. Caso contrario:
         a) Se permitir_repetidos=True e intervalo k = max - min + 1
            for suficientemente pequeno (k <= n * log2(n) / 2),
            utiliza Counting Sort (O(n+k) linear).
         b) Se n <= 50, utiliza Insertion Sort (secundario para
            entradas muito pequenas, onde o overhead do Quicksort
            nao compensa).
         c) Caso geral: utiliza Quicksort (algoritmo principal),
            que apresentou o melhor desempenho geral nos benchmarks
            para entradas aleatorias e decrescentes em ambos os
            cenarios (com e sem elementos repetidos).

    Anãlise dos dados (10 tamanhos x 3 condicoes, 10 repeticoes cada, totalizando 2630 resultados):
      - Quicksort: melhor tempo medio para a maioria dos cenarios
        (aleatorio e decrescente) a partir de n >= 500. Para n=50/100,
        Insertion Sort e competitivo.
      - Mergesort: desempenho muito proximo ao Quicksort, porem
        consistentemente um pouco pior em tempo. Seria a alternativa
        caso o pior caso O(n^2) do Quicksort fosse uma preocupacao.
      - Heapsort: consistentemente pior que Quicksort e Mergesort
        em todos os cenarios testados, por isso foi descartado.
      - Counting Sort: para vetores com elementos repetidos gerados
        em intervalo restrito (amostras com reposicao de 1..n),
        o intervalo k tende a ser muito menor que n*log(n),
        tornando o algoritmo linear extremamente vantajoso.
        Ex: n=200000, k medio ~ 20000, O(n+k)=220K vs O(n log n)~3.5M.
      - Insertion Sort: O(n^2) no caso medio, porem extremamente
        rapido para n <= 50. Dados confirmam que e o melhor para n=50 em varios
        cenarios.

    Parametros:
      vetor: lista de inteiros a ser ordenada.
      permitir_repetidos: booleano indicando se o vetor pode conter
                          elementos repetidos (default=False).

    Retorna:
      (vetor_ordenado, comparacoes): tupla com o vetor ordenado e
      o numero total de comparacoes realizadas.
    """
    arr = list(vetor)
    n = len(arr)
    comparacoes = 0

    if n <= 1:
        return arr, 0
    #TODO: verificar uma forma de detectar o caso de elementos repetidos sem
    # precisar da flag permitir_repetidos, para nao penalizar o caso sem repetidos. 
    # Talvez uma varredura inicial O(n) que detecta se ha repetidos e coleta min/max, 
    # e entao decide sobre o uso do Counting Sort. 
    # Assim, o algoritmo se adaptaria dinamicamente a ambos os casos, sem exigir um parametro externo.

    # ---------------------------------------------------------------
    # Etapa 1: Varredura de diagnostico O(n)
    # Verifica se o vetor ja esta ordenado em ordem crescente e,
    # quando permitir_repetidos=True, coleta min e max para
    # decidir sobre o Counting Sort.
    # ---------------------------------------------------------------
    ordenado_crescente = True
    minimo = arr[0]
    maximo = arr[0]

    for i in range(1, n):
        comparacoes += 1
        if arr[i] < arr[i - 1]:
            ordenado_crescente = False

        if arr[i] < minimo:
            minimo = arr[i]
        if arr[i] > maximo:
            maximo = arr[i]

    # ---------------------------------------------------------------
    # Etapa 2: Se ja estiver crescente, retorna imediatamente.
    # ---------------------------------------------------------------
    if ordenado_crescente:
        return arr, comparacoes

    # ---------------------------------------------------------------
    # Etapa 3: Decisao do algoritmo de ordenacao.
    # ---------------------------------------------------------------

    # 3a. Counting Sort para vetores com repetidos e intervalo pequeno.
    if permitir_repetidos:
        k = maximo - minimo + 1
        # Threshold: so usa Counting Sort se O(n+k) < O(n log n)/2
        # n * log2(n) / 2 e um limite conservador que garante vantagem
        # significativa do algoritmo linear sobre os O(n log n).
        limiar = n * math.log2(n) / 2 if n > 1 else 0
        if k <= limiar:
            arr_ordenado, comps_counting = ordenar_countingsort(arr)
            comparacoes += comps_counting
            return arr_ordenado, comparacoes

    # 3b. Insertion Sort para entradas muito pequenas (n <= 50).
    if n <= 50:
        arr_ordenado, comps_insertion = ordenar_insertionsort(arr)
        comparacoes += comps_insertion
        return arr_ordenado, comparacoes

    # 3c. Quicksort como algoritmo principal para os demais casos.
    arr_ordenado, comps_quick = ordenar_quicksort(arr)
    comparacoes += comps_quick
    return arr_ordenado, comparacoes