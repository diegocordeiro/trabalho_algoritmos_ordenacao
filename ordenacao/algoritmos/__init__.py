from .bublesort import ordenar_bublesort
from .heap import ordenar_heap
from .insertionsort import ordenar_insertionsort
from .mergesort import ordenar_mergesort
from .quicksort import ordenar_quicksort

ALGORITMOS = {
    'bublesort': ordenar_bublesort,
    'insertionsort': ordenar_insertionsort,
    'mergesort': ordenar_mergesort,
    'heap': ordenar_heap,
    'quicksort': ordenar_quicksort,
}
