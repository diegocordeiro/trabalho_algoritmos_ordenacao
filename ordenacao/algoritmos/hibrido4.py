from .countingsort import ordenar_countingsort
from .mergesort import ordenar_mergesort
from .quicksort import ordenar_quicksort


def ordenar_hibrido4(vetor):
    """
    Algoritmo hibrido 4 de ordenacao que seleciona a melhor estrategia com base
    na caracteristica do vetor de entrada.

    Estrategia:
      1. Varredura linear O(n) para classificar o vetor como:
         crescente, decrescente ou aleatorio.
      2. Crescente (qualquer n) -> retorna imediatamente.
      3. Decrescente (qualquer n) -> MergeSort puro.
      4. Aleatorio:
         - n <= 50 -> Counting Sort (pre-ordenacao agrupando valores iguais)
           seguido de MergeSort.
         - n > 50  -> QuickSort puro com pivo randomizado.

    Diferentemente do hibrido3, este algoritmo NAO aplica Counting Sort
    como pre-processamento para vetores decrescentes nem para vetores
    aleatorios com n > 50. O Counting Sort e utilizado apenas para
    vetores aleatorios pequenos (n <= 50) para agrupar valores iguais
    antes do MergeSort.
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

    # Caso 2: Vetor decrescente -> MergeSort puro (sem Counting Sort)
    if estritamente_decrescente:
        arr, comps_ms = ordenar_mergesort(arr)
        comparacoes += comps_ms
        return arr, comparacoes

    # Caso 3: Vetor aleatorio com n <= 50 ->
    # Pre-ordenacao com Counting Sort (agrupa valores iguais)
    # seguido de MergeSort
    if n <= 50:
        arr, comps_cs = ordenar_countingsort(arr)
        comparacoes += comps_cs  # Counting Sort nao adiciona comparacoes (0)
        arr, comps_ms = ordenar_mergesort(arr)
        comparacoes += comps_ms
        return arr, comparacoes

    # Caso 4: Vetor aleatorio com n > 50 ->
    # QuickSort puro (sem Counting Sort)
    arr, comps_qs = ordenar_quicksort(arr)
    comparacoes += comps_qs
    return arr, comparacoes