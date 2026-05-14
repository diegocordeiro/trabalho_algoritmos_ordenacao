import csv
import statistics
from collections import defaultdict

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from benchmark.models import ExecucaoBenchmark, ResultadoExecucao
from benchmark.services import _filtrar_outliers


def _fmt(valor, casas=4):
    """
    Formata números float com número fixo de casas decimais.
    Trata None de forma segura.
    """
    if valor is None:
        return ''
    return f'{valor:.{casas}f}'


def _gerar_csv_resultados(resultados_qs, nome_arquivo, incluir_execucao=False):
    """
    Gera CSV com métricas estatísticas filtradas (sem outliers).
    Agrupa resultados por algoritmo, condicao, tamanho (e execucao_id se aplicável),
    aplica _filtrar_outliers nos tempos e comparações, e computa CV filtrado.
    """
    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    resposta['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

    writer = csv.writer(resposta)

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
        'n_original',
        'n_filtrado_tempo',
        'n_filtrado_comp',
        'permitir_repetidos',
    ])
    writer.writerow(cabecalho)

    # Agrupa resultados por chave de combinação
    grupos = defaultdict(list)
    for r in resultados_qs:
        if incluir_execucao:
            chave = (r.execucao_id, r.algoritmo, r.condicao, r.tamanho)
        else:
            chave = (r.algoritmo, r.condicao, r.tamanho)
        grupos[chave].append(r)

    for chave, itens in sorted(grupos.items()):
        amostra = itens[0]
        permitir_repetidos = amostra.execucao.permitir_repetidos
        tempos = [r.tempo_ms for r in itens]
        comparacoes = [r.comparacoes for r in itens]

        n_original = len(itens)

        # --- FILTRAGEM DE OUTLIERS ---
        tempos_filt, removeu_tempo = _filtrar_outliers(tempos)
        comps_filt, removeu_comp = _filtrar_outliers(comparacoes)

        # --- TEMPO (com outliers removidos se aplicável) ---
        if removeu_tempo and len(tempos_filt) >= 2:
            media_tempo = statistics.mean(tempos_filt)
            std_tempo = statistics.stdev(tempos_filt)
            cv_tempo = (std_tempo / media_tempo * 100) if media_tempo > 0 else 0
            n_filt_tempo = len(tempos_filt)
        else:
            media_tempo = statistics.mean(tempos)
            std_tempo = statistics.stdev(tempos) if len(tempos) > 1 else 0
            cv_tempo = (std_tempo / media_tempo * 100) if media_tempo > 0 else 0
            n_filt_tempo = n_original

        if cv_tempo <= 10:
            classe_cv_tempo = 'Muito Baixa Variação'
        elif cv_tempo <= 20:
            classe_cv_tempo = 'Moderada Variação'
        elif cv_tempo <= 30:
            classe_cv_tempo = 'Alta Variação'
        else:
            classe_cv_tempo = 'Variação Muito Alta'

        # --- COMPARAÇÕES (com outliers removidos se aplicável) ---
        if removeu_comp and len(comps_filt) >= 2:
            media_comp = statistics.mean(comps_filt)
            std_comp = statistics.stdev(comps_filt)
            cv_comp = (std_comp / media_comp * 100) if media_comp > 0 else 0
            n_filt_comp = len(comps_filt)
        else:
            media_comp = statistics.mean(comparacoes)
            std_comp = statistics.stdev(comparacoes) if len(comparacoes) > 1 else 0
            cv_comp = (std_comp / media_comp * 100) if media_comp > 0 else 0
            n_filt_comp = n_original

        if cv_comp <= 10:
            classe_cv_comp = 'Muito Baixa Variação'
        elif cv_comp <= 20:
            classe_cv_comp = 'Moderada Variação'
        elif cv_comp <= 30:
            classe_cv_comp = 'Alta Variação'
        else:
            classe_cv_comp = 'Variação Muito Alta'

        linha = []
        if incluir_execucao:
            linha.append(chave[0])  # execucao_id
            linha.extend([
                chave[1],  # algoritmo
                chave[2],  # condicao
                chave[3],  # tamanho
            ])
        else:
            linha.extend([
                chave[0],  # algoritmo
                chave[1],  # condicao
                chave[2],  # tamanho
            ])

        linha.extend([
            _fmt(media_tempo),
            _fmt(std_tempo),
            _fmt(cv_tempo, 2),
            classe_cv_tempo,
            _fmt(media_comp),
            n_original,
            n_filt_tempo,
            n_filt_comp,
            'Sim' if permitir_repetidos else 'Nao',
        ])
        writer.writerow(linha)

    return resposta


def exportar_csv(request, execucao_id):
    """
    Exporta uma execução com estatísticas filtradas (sem outliers).
    """
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)

    resultados = ResultadoExecucao.objects.filter(execucao=execucao).order_by('algoritmo', 'condicao', 'tamanho')

    return _gerar_csv_resultados(
        resultados,
        f'resultados_execucao_{execucao_id}.csv',
        incluir_execucao=False
    )


@require_POST
def exportar_csv_selecionadas(request):
    """
    Exporta múltiplas execuções no mesmo formato estatístico filtrado (sem outliers).
    """
    ids = request.POST.getlist('execucoes')

    if not ids:
        return HttpResponseBadRequest('Selecione ao menos uma execução.')

    resultados = ResultadoExecucao.objects.filter(execucao_id__in=ids).order_by('execucao_id', 'algoritmo', 'condicao', 'tamanho')

    return _gerar_csv_resultados(
        resultados,
        'resultados_estatisticos_selecionados.csv',
        incluir_execucao=True
    )