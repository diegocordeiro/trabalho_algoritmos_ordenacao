from .insertionsort import ordenar_insertionsort
from .mergesort import ordenar_mergesort
from .quicksort import ordenar_quicksort


def ordenar_hibrido(vetor):
    """
    Algoritmo hibrido de ordenacao que seleciona a melhor estrategia com base
    na caracteristica do vetor de entrada, com base nos dados experimentais
    de benchmark.

    Estrategia:
      1. Varredura linear O(n) para classificar o vetor como:
         crescente, decrescente ou aleatorio.
      2. Crescente (qualquer n) -> retorna imediatamente.
         InsertionSort ja faria O(n) nesse cenario; a varredura de deteccao
         ja realizou o trabalho equivalente, portanto retornar imediatamente
         e a decisao otima.
      3. Decrescente (qualquer n) -> MergeSort.
         - O(n log n) garantido no pior caso (QuickSort pode degradar para
           O(n^2) se a escolha de pivo for desfavoravel).
         - 2.5x menos comparacoes que QuickSort nesse cenario
           (ex: n=200.000 decrescente: mergesort 1.730.048 comps vs
            quicksort 4.382.103 comps).
         - Menor variabilidade (CV 1.8% vs 3.9% do QuickSort).
      4. Aleatorio (qualquer n) -> QuickSort com pivo randomizado.
         - Melhor tempo de execucao em todos os tamanhos testados
           (ex: n=100 aleatorio: quicksort 0.048ms vs insertionsort 0.109ms;
            n=500 aleatorio: quicksort 0.311ms vs insertionsort 2.694ms;
            n=200.000 aleatorio: quicksort 219.42ms vs mergesort 345.19ms).
         - Excelente localidade de cache (particionamento local).
         - Baixo overhead por chamada recursiva, apenas para construir o heap inicial e reorganizar apõs a remoção.
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
        arr, comps = ordenar_mergesort(arr)
        comparacoes += comps
        return arr, comparacoes

    # Caso 3: Vetor aleatorio -> QuickSort com pivo randomico
    arr, comps = ordenar_quicksort(arr)
    comparacoes += comps
    return arr, comparacoes
