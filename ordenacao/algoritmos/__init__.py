from .bolha import ordenar_bolha
from .heap import ordenar_heap
from .insercao import ordenar_insercao
from .intercalacao import ordenar_intercalacao
from .rapido import ordenar_rapido

ALGORITMOS = {
    'bolha': ordenar_bolha,
    'insercao': ordenar_insercao,
    'intercalacao': ordenar_intercalacao,
    'heap': ordenar_heap,
    'rapido': ordenar_rapido,
}
