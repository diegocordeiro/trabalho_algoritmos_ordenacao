from .bublesort import ordenar_bublesort
from .heap import ordenar_heap
from .insertionsort import ordenar_insertionsort
from .mergesort import ordenar_mergesort
from .quicksort import ordenar_quicksort

ALGORITMOS = {
    'bolha': ordenar_bublesort,
    'insercao': ordenar_insertionsort,
    'intercalacao': ordenar_mergesort,
    'heap': ordenar_heap,
    'rapido': ordenar_quicksort,
}
