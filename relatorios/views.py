import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from benchmark.models import ExecucaoBenchmark, ResultadoExecucao
from benchmark.services import medias_por_combinacao


def exportar_csv(request, execucao_id):
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)
    resposta = HttpResponse(content_type='text/csv')
    resposta['Content-Disposition'] = f'attachment; filename="resultados_execucao_{execucao_id}.csv"'
    writer = csv.writer(resposta)
    writer.writerow(['algoritmo', 'condicao', 'tamanho', 'rodada', 'tempo_ms', 'comparacoes'])
    for item in ResultadoExecucao.objects.filter(execucao=execucao):
        writer.writerow([item.algoritmo, item.condicao, item.tamanho, item.rodada, item.tempo_ms, item.comparacoes])
    return resposta