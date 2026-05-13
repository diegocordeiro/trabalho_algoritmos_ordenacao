from .countingsort import ordenar_countingsort
from .mergesort import ordenar_mergesort
from .quicksort import ordenar_quicksort


def ordenar_hibrido3(vetor):
    """
    Algoritmo hibrido 3 de ordenacao que seleciona a melhor estrategia com base
    na caracteristica do vetor de entrada.

    Estrategia:
      1. Varredura linear O(n) para classificar o vetor como:
         crescente, decrescente ou aleatorio.
      2. Crescente (qualquer n) -> retorna imediatamente.
      3. Nao crescente -> Counting Sort (pre-ordenacao agrupando valores iguais).
         Apos o Counting Sort:
         - Decrescente -> MergeSort.
         - Aleatorio:
           - n <= 50 -> MergeSort (eficiente para vetores pequenos).
           - n > 50  -> QuickSort com pivo randomizado.

    A pre-ordenacao com Counting Sort agrupa valores iguais antes de aplicar
    o MergeSort ou QuickSort, reduzindo a quantidade de comparacoes necessarias
    nas etapas posteriores.
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

    # Caso 2 e 3: Vetor nao crescente ->
    # Pre-ordenacao com Counting Sort (agrupa valores iguais)
    arr, comps_cs = ordenar_countingsort(arr)
    comparacoes += comps_cs  # Counting Sort nao adiciona comparacoes (0)

    # Decisao pos Counting Sort:
    # - Decrescente -> MergeSort
    # - Aleatorio:
    #   - n <= 50 -> MergeSort
    #   - n > 50  -> QuickSort
    if estritamente_decrescente or n <= 50:
        arr, comps_ms = ordenar_mergesort(arr)
        comparacoes += comps_ms
    else:
        arr, comps_qs = ordenar_quicksort(arr)
        comparacoes += comps_qs

    return arr, comparacoes