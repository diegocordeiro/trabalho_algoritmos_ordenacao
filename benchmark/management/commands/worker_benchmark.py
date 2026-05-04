import time

from django.core.management.base import BaseCommand

from benchmark.models import ExecucaoBenchmark
from benchmark.services import executar_benchmark


class Command(BaseCommand):
    help = 'Worker serial para processar fila de execuções pendentes (uma por vez).'

    def add_arguments(self, parser):
        parser.add_argument('--sleep', type=float, default=1.0, help='Intervalo entre polls quando não há itens pendentes.')
        parser.add_argument('--once', action='store_true', help='Processa no máximo uma execução pendente e encerra.')

    def handle(self, *args, **options):
        intervalo = options['sleep']
        executar_uma_vez = options['once']
        self.stdout.write(self.style.WARNING('Worker serial iniciado.'))

        while True:
            execucao = (
                ExecucaoBenchmark.objects.filter(status='pendente')
                .order_by('criado_em', 'id')
                .first()
            )

            if execucao is None:
                if executar_uma_vez:
                    self.stdout.write(self.style.WARNING('Nenhuma execução pendente encontrada.'))
                    return
                time.sleep(intervalo)
                continue

            self.stdout.write(f'Processando execução #{execucao.id}...')
            executar_benchmark(execucao.id)
            self.stdout.write(self.style.SUCCESS(f'Execução #{execucao.id} finalizada.'))

            if executar_uma_vez:
                return
