from django.core.management.base import BaseCommand

from benchmark.models import ExecucaoBenchmark
from benchmark.services import executar_benchmark


class Command(BaseCommand):
    help = 'Executa benchmark da Parte I com os parametros informados.'

    def add_arguments(self, parser):
        parser.add_argument('--algoritmos', default='bublesort,insertionsort,mergesort,heap,quicksort')
        parser.add_argument('--condicoes', default='crescente,decrescente,aleatorio')
        parser.add_argument('--tamanhos', default='500')
        parser.add_argument('--repeticoes', type=int, default=3)
        parser.add_argument('--nome', default='Execucao Parte I')
        parser.add_argument('--vetor-personalizado', default='')

    def handle(self, *args, **options):
        algoritmos = [item.strip() for item in options['algoritmos'].split(',') if item.strip()]
        condicoes = [item.strip() for item in options['condicoes'].split(',') if item.strip()]
        tamanhos = [int(item.strip()) for item in options['tamanhos'].split(',') if item.strip()]
        execucao = ExecucaoBenchmark.objects.create(
            nome=options['nome'],
            algoritmos=algoritmos,
            condicoes=condicoes,
            tamanhos=tamanhos,
            repeticoes=options['repeticoes'],
            vetor_personalizado=options['vetor_personalizado'],
            status='pendente',
            progresso_texto='Aguardando inicio...',
        )
        executar_benchmark(execucao.id)
        execucao.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(f'Execucao {execucao.id} finalizada com status: {execucao.status}'))
