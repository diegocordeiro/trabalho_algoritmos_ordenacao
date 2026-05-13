from .countingsort import ordenar_countingsort
from .insertionsort import ordenar_insertionsort
from .quicksort import ordenar_quicksort


def ordenar_hibrido2(vetor):
    """
    Algoritmo hibrido 2 de ordenacao que seleciona a melhor estrategia com base
    na caracteristica do vetor de entrada.

    Estrategia:
      1. Varredura linear O(n) para classificar o vetor como:
         crescente, decrescente ou aleatorio.
      2. Crescente (qualquer n) -> retorna imediatamente.
      3. Decrescente -> Counting Sort (pre-ordenacao agrupando valores iguais)
         seguido de QuickSort com pivo randomizado.
      4. Aleatorio:
         - n <= 100 -> InsertionSort (eficiente para vetores pequenos).
         - n > 100  -> Counting Sort (pre-ordenacao agrupando valores iguais)
           seguido de QuickSort com pivo randomizado.

    A pre-ordenacao com Counting Sort agrupa valores iguais antes de aplicar
    o QuickSort, reduzindo a quantidade de comparacoes necessarias na etapa
    de particionamento.
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

    # Caso 2: Vetor aleatorio com ate 100 posicoes -> InsertionSort
    if not estritamente_decrescente and n <= 100:
        arr, comps_is = ordenar_insertionsort(arr)
        comparacoes += comps_is
        return arr, comparacoes

    # Caso 3 e 4: Vetor decrescente (qualquer n) ou
    # aleatorio com n > 100 ->
    # Pre-ordenacao com Counting Sort (agrupa valores iguais)
    # seguido de QuickSort com pivo randomizado
    arr, comps_cs = ordenar_countingsort(arr)
    comparacoes += comps_cs  # Counting Sort nao adiciona comparacoes (0)

    arr, comps_qs = ordenar_quicksort(arr)
    comparacoes += comps_qs

    return arr, comparacoes
