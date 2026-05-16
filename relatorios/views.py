import csv

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from benchmark.models import ExecucaoBenchmark, ResultadoExecucao


def _gerar_csv_resultados(resultados_qs, nome_arquivo, incluir_execucao=False, incluir_media=True):
    """
    Gera CSV com os dados detalhados por rodada (algoritmo, condicao, tamanho, rodada,
    tempo_ms, comparacoes, permitir_repetidos). Inclui uma linha de MEDIA ao final de
    cada grupo (algoritmo + condicao + tamanho [+ execucao_id se incluir_execucao])
    quando incluir_media=True.
    """
    resultados = resultados_qs.order_by(
        'algoritmo', 'condicao', 'tamanho', 'rodada'
    )

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
        'rodada',
        'tempo_ms',
        'comparacoes',
        'permitir_repetidos',
    ])
    writer.writerow(cabecalho)

    grupo_atual = None
    tempos_grupo = []
    comps_grupo = []
    permitir_repetidos_valor = 'Nao'

    def _escrever_media():
        """Escreve a linha de media para o grupo acumulado."""
        media_tempo = sum(tempos_grupo) / len(tempos_grupo)
        media_comp = sum(comps_grupo) / len(comps_grupo)
        linha = []
        if incluir_execucao:
            linha.append(grupo_atual[0])
            linha.extend([
                grupo_atual[1],
                grupo_atual[2],
                grupo_atual[3],
            ])
        else:
            linha.extend([
                grupo_atual[0],
                grupo_atual[1],
                grupo_atual[2],
            ])
        linha.extend([
            f'MEDIA (n={len(tempos_grupo)})',
            f'{media_tempo:.2f}',
            f'{media_comp:.2f}',
            permitir_repetidos_valor,
        ])
        writer.writerow(linha)

    for r in resultados:
        if incluir_execucao:
            chave = (r.execucao_id, r.algoritmo, r.condicao, r.tamanho)
        else:
            chave = (r.algoritmo, r.condicao, r.tamanho)

        # Se mudou o grupo, escreve a media do grupo anterior
        if incluir_media and grupo_atual is not None and chave != grupo_atual:
            _escrever_media()
            tempos_grupo = []
            comps_grupo = []

        grupo_atual = chave
        permitir_repetidos_valor = 'Sim' if r.execucao.permitir_repetidos else 'Nao'
        tempos_grupo.append(r.tempo_ms)
        comps_grupo.append(r.comparacoes)

        linha = []
        if incluir_execucao:
            linha.append(r.execucao_id)
        linha.extend([
            r.algoritmo,
            r.condicao,
            r.tamanho,
            r.rodada,
            f'{r.tempo_ms:.2f}',
            f'{r.comparacoes:.2f}',
            permitir_repetidos_valor,
        ])
        writer.writerow(linha)

    # Escreve a media do ultimo grupo
    if incluir_media and grupo_atual is not None and tempos_grupo:
        _escrever_media()

    return resposta


def exportar_csv(request, execucao_id):
    """
    Exporta uma execucao no formato por rodada (algoritmo, condicao, tamanho, rodada,
    tempo_ms, comparacoes, permitir_repetidos) com linha de MEDIA ao final de cada grupo.
    """
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)

    resultados = ResultadoExecucao.objects.filter(execucao=execucao)

    return _gerar_csv_resultados(
        resultados,
        f'resultados_execucao_{execucao_id}.csv',
        incluir_execucao=False
    )


@require_POST
def exportar_csv_selecionadas(request):
    """
    Exporta multiplas execucoes no formato por rodada (algoritmo, condicao, tamanho,
    rodada, tempo_ms, comparacoes, permitir_repetidos), incluindo coluna execucao_id.
    Sem linha de MEDIA ao final de cada grupo.
    """
    ids = request.POST.getlist('execucoes')

    if not ids:
        return HttpResponseBadRequest('Selecione ao menos uma execução.')

    resultados = ResultadoExecucao.objects.filter(execucao_id__in=ids)

    return _gerar_csv_resultados(
        resultados,
        'resultados_estatisticos_selecionados.csv',
        incluir_execucao=True,
        incluir_media=False
    )
