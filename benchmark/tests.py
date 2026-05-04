from django.test import TestCase

from ordenacao.algoritmos import ALGORITMOS


class AlgoritmosOrdenacaoTestCase(TestCase):
    def test_algoritmos_ordenam_crescente(self):
        entrada = [1, 2, 3, 4, 5]
        for nome, algoritmo in ALGORITMOS.items():
            ordenado, comparacoes = algoritmo(entrada)
            self.assertEqual(ordenado, sorted(entrada), msg=nome)
            self.assertGreaterEqual(comparacoes, 0, msg=nome)

    def test_algoritmos_ordenam_decrescente(self):
        entrada = [5, 4, 3, 2, 1]
        for nome, algoritmo in ALGORITMOS.items():
            ordenado, comparacoes = algoritmo(entrada)
            self.assertEqual(ordenado, sorted(entrada), msg=nome)
            self.assertGreaterEqual(comparacoes, 0, msg=nome)

    def test_algoritmos_ordenam_aleatorio(self):
        entrada = [9, 1, 7, 3, 6, 2, 8, 4, 5]
        for nome, algoritmo in ALGORITMOS.items():
            ordenado, comparacoes = algoritmo(entrada)
            self.assertEqual(ordenado, sorted(entrada), msg=nome)
            self.assertGreaterEqual(comparacoes, 0, msg=nome)
