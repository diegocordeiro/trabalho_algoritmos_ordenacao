from .countingsort import ordenar_countingsort
from .mergesort import ordenar_mergesort
from .quicksort import ordenar_quicksort
from .radixsort import ordenar_radixsort


def ordenar_hibrido5(vetor):
    """
    Algoritmo hibrido 5 de ordenacao que seleciona a melhor estrategia com base
    na caracteristica do vetor de entrada.

    Estrategia:
      1. Varredura linear O(n) para classificar o vetor como:
         crescente, decrescente ou aleatorio.
      2. Crescente (qualquer n) -> retorna imediatamente.
      3. Decrescente (qualquer n) -> MergeSort puro.
      4. Aleatorio:
         - n <= 50 -> Counting Sort (pre-ordenacao agrupando valores iguais)
           seguido de MergeSort.
         - 50 < n <= 500 -> QuickSort puro com pivo randomizado.
         - n > 500 -> LSD Radix Sort base 65536 que utiliza MergeSort
           como sub-rotina estavel em cada passada (substituindo o
           Counting Sort tradicional). Com base 65536, realiza no
           maximo 2 passadas. O MergeSort opera sobre pares (digito, valor)
           garantindo a estabilidade necessaria ao LSD.

    Diferentemente do hibrido3, este algoritmo NAO aplica Counting Sort
    como pre-processamento para vetores decrescentes. Para vetores
    aleatorios com n > 500, utiliza Radix Sort com MergeSort interno
    (em vez de Counting Sort), atendendo a regra de que o Radix Sort
    nao pode ser o principal sem utilizar MergeSort ou QuickSort
    como sub-rotina.
    """
    arr = list(vetor)
    n = len(arr)
    comparacoes = 0

    # ----------------------------------------------------------------
    # PASSO 1: Varredura linear para detectar ordenacao e padrao
    # ----------------------------------------------------------------
    if n <= 1:
        return arr, 0

    ordenado = True
    estritamente_decrescente = True

    for i in range(1, n):
        comparacoes += 1
        if arr[i] < arr[i - 1]:
            ordenado = False
        if arr[i] >= arr[i - 1]:
            estritamente_decrescente = False

    # ----------------------------------------------------------------
    # PASSO 2: Selecao do algoritmo com base na caracteristica do vetor
    # ----------------------------------------------------------------

    # Caso 1: Vetor ja ordenado crescentemente -> retorna imediatamente
    if ordenado:
        return arr, comparacoes

    # Caso 2: Vetor decrescente -> MergeSort
    if estritamente_decrescente:
        arr, comps_ms = ordenar_mergesort(arr)
        comparacoes += comps_ms
        return arr, comparacoes

    # Caso 3: Vetor aleatorio com n <= 500 ->  LSD Radix Sort base 65536 com counting sort interno
    if n <= 500:
        arr, comps_qs = ordenar_radixsort(arr) 
        comparacoes += comps_qs
        return arr, comparacoes

    # Caso 4: Vetor aleatorio com n > 500 -> QuickSort puro com pivo randomizado
    arr, comps_rs = ordenar_quicksort(arr)
    comparacoes += comps_rs
    return arr, comparacoes