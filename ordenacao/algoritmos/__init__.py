from .bublesort import ordenar_bublesort
from .countingsort import ordenar_countingsort
from .heap import ordenar_heap
from .hibrido import ordenar_hibrido
from .hibrido2 import ordenar_hibrido2
from .hibrido3 import ordenar_hibrido3
from .hibrido4 import ordenar_hibrido4
from .hibrido5 import ordenar_hibrido5
from .insertionsort import ordenar_insertionsort
from .mergesort import ordenar_mergesort
from .quicksort import ordenar_quicksort
from .radixsort import ordenar_radixsort

ALGORITMOS = {
    'bublesort': ordenar_bublesort,
    'countingsort': ordenar_countingsort,
    'insertionsort': ordenar_insertionsort,
    'mergesort': ordenar_mergesort,
    'heap': ordenar_heap,
    'quicksort': ordenar_quicksort,
    'radixsort': ordenar_radixsort,
    'hibrido': ordenar_hibrido,
    'hibrido2': ordenar_hibrido2,
    'hibrido3': ordenar_hibrido3,
    'hibrido4': ordenar_hibrido4,
    'hibrido5': ordenar_hibrido5,
}
