from django.core.management.base import BaseCommand

from benchmark.models import ExecucaoBenchmark
from benchmark.services import executar_benchmark, gerar_csv_resultados_arquivo


class Command(BaseCommand):
    help = 'Executa benchmark da Parte I com os parâmetros informados (uma execução por algoritmo).'

    def add_arguments(self, parser):
        parser.add_argument('--algoritmos', default='bublesort,insertionsort,mergesort,heap,quicksort')
        parser.add_argument('--condicoes', default='crescente,decrescente,aleatorio')
        parser.add_argument('--tamanhos', default='500')
        parser.add_argument('--repeticoes', type=int, default=3)
        parser.add_argument('--nome', default='')
        parser.add_argument('--vetor-personalizado', default='')

    def handle(self, *args, **options):
        nomes_algoritmos = [item.strip() for item in options['algoritmos'].split(',') if item.strip()]
        condicoes = [item.strip() for item in options['condicoes'].split(',') if item.strip()]
        tamanhos = [int(item.strip()) for item in options['tamanhos'].split(',') if item.strip()]

        for algoritmo in nomes_algoritmos:
            execucao = ExecucaoBenchmark.objects.create(
                nome=f"{algoritmo} :: Tamanho {options['tamanhos']}".strip(),
                algoritmos=[algoritmo],
                condicoes=condicoes,
                tamanhos=tamanhos,
                repeticoes=options['repeticoes'],
                vetor_personalizado=options['vetor_personalizado'],
                status='pendente',
                progresso_texto='Iniciando...',
            )

            self.stdout.write(f'[{algoritmo}] Execução #{execucao.id} iniciada...')

            executar_benchmark(execucao.id)
            execucao.refresh_from_db()

            if execucao.status == 'concluido':
                caminho_csv = gerar_csv_resultados_arquivo(execucao.id)
                self.stdout.write(self.style.SUCCESS(f'[{algoritmo}] CSV gerado em: {caminho_csv}'))
            else:
                self.stdout.write(self.style.ERROR(f'[{algoritmo}] Falhou com status: {execucao.status}'))

            self.stdout.write(f'[{algoritmo}] Execução #{execucao.id} finalizada: {execucao.status}')

        self.stdout.write(self.style.SUCCESS(f'{len(nomes_algoritmos)} execuções concluídas.'))