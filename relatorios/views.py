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
    primeiro = resultados[0] if resultados else None
    incluir_execucao = bool(primeiro and 'execucao_id' in primeiro)

    cabecalho = []
    if incluir_execucao:
        cabecalho.append('execucao_id')
    cabecalho.extend([
        'algoritmo',
        'condicao',
        'tamanho',
        'media_tempo_ms',
        'std_tempo_ms',
        'cv_tempo_pct',
        'classe_cv_tempo',
        'media_comparacoes',
        'std_comparacoes',
        'cv_comparacoes_pct',
        'classe_cv_comparacoes',
        'n'
    ])
    writer.writerow(cabecalho)

    for item in resultados:
        media_tempo = item['media_tempo_ms'] or 0
        std_tempo = item['std_tempo_ms'] or 0
        cv_tempo = (std_tempo / media_tempo * 100) if media_tempo > 0 else 0
        if cv_tempo < 5:
            classe_cv_tempo = 'muito estável'
        elif cv_tempo <= 15:
            classe_cv_tempo = 'aceitável'
        else:
            classe_cv_tempo = 'instável'

        media_comp = item['media_comparacoes'] or 0
        std_comp = item['std_comparacoes'] or 0
        cv_comp = (std_comp / media_comp * 100) if media_comp > 0 else 0
        if cv_comp < 5:
            classe_cv_comp = 'muito estável'
        elif cv_comp <= 15:
            classe_cv_comp = 'aceitável'
        else:
            classe_cv_comp = 'instável'

        linha = []
        if incluir_execucao:
            linha.append(item['execucao_id'])
        linha.extend([
            item['algoritmo'],
            item['condicao'],
            item['tamanho'],
            _fmt(media_tempo),
            _fmt(std_tempo),
            _fmt(cv_tempo, 2),
            classe_cv_tempo,
            _fmt(media_comp),
            _fmt(std_comp),
            _fmt(cv_comp, 2),
            classe_cv_comp,
            item['n'],
        ])
        writer.writerow(linha)

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
    Exporta múltiplas execuções no mesmo formato estatístico do CSV individual.
    """
    ids = request.POST.getlist('execucoes')

    if not ids:
        return HttpResponseBadRequest('Selecione ao menos uma execução.')

    resultados = list(
        ResultadoExecucao.objects
        .filter(execucao_id__in=ids)
        .values('execucao_id', 'algoritmo', 'condicao', 'tamanho')
        .annotate(
            media_tempo_ms=Avg('tempo_ms'),
            std_tempo_ms=StdDev('tempo_ms'),
            media_comparacoes=Avg('comparacoes'),
            std_comparacoes=StdDev('comparacoes'),
            n=Count('id')
        )
        .order_by('execucao_id', 'algoritmo', 'condicao', 'tamanho')
    )

    return _gerar_csv_resultados(
        resultados,
        'resultados_estatisticos_selecionados.csv'
    )
