import csv

from django.db.models import Avg, StdDev, Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from benchmark.models import ExecucaoBenchmark, ResultadoExecucao


def _fmt(valor, casas=4):
    """
    Formata números float com número fixo de casas decimais.
    Trata None de forma segura.
    """
    if valor is None:
        return ''
    return f'{valor:.{casas}f}'


def _gerar_csv_resultados(resultados, nome_arquivo):
    """
    Gera CSV com métricas estatísticas.
    StdDev (desvio padrão)
    Count (número de amostras)
    Controle de casas decimais no CSV
    Média hierárquica (por execução → depois global)
    """
    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    resposta['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

    writer = csv.writer(resposta)
    writer.writerow([
        'algoritmo',
        'condicao',
        'tamanho',
        'media_tempo_ms',
        'std_tempo_ms',
        'media_comparacoes',
        'std_comparacoes',
        'n'
    ])

    for item in resultados:
        writer.writerow([
            item['algoritmo'],
            item['condicao'],
            item['tamanho'],
            _fmt(item['media_tempo_ms']),
            _fmt(item['std_tempo_ms']),
            _fmt(item['media_comparacoes']),
            _fmt(item['std_comparacoes']),
            item['n'],
        ])

    return resposta


def _query_agregada(filtro):
    """
    Centraliza a lógica de agregação.
    """
    return (
        ResultadoExecucao.objects
        .filter(**filtro)
        .values('algoritmo', 'condicao', 'tamanho')
        .annotate(
            media_tempo_ms=Avg('tempo_ms'),
            std_tempo_ms=StdDev('tempo_ms'),
            media_comparacoes=Avg('comparacoes'),
            std_comparacoes=StdDev('comparacoes'),
            n=Count('id')
        )
        .order_by('algoritmo', 'condicao', 'tamanho')
    )


def exportar_csv(request, execucao_id):
    """
    Exporta uma execução com estatísticas completas.
    """
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)

    resultados = _query_agregada({'execucao': execucao})

    return _gerar_csv_resultados(
        resultados,
        f'resultados_execucao_{execucao_id}.csv'
    )


@require_POST
def exportar_csv_selecionadas(request):
    """
    Exporta múltiplas execuções com estatísticas consolidadas.
    """
    ids = request.POST.getlist('execucoes')

    if not ids:
        return HttpResponseBadRequest('Selecione ao menos uma execução.')

    resultados = _query_agregada({'execucao_id__in': ids})

    return _gerar_csv_resultados(
        resultados,
        'resultados_estatisticos_selecionados.csv'
    )