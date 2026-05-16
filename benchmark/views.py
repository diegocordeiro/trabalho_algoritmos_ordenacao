import statistics
from collections import defaultdict

import scipy.stats as st
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Avg, FloatField
from django.db.models.functions import Round, Cast

from benchmark.forms import ConfiguracaoBenchmarkForm
from benchmark.models import BenchmarkConfig, ExecucaoBenchmark, ResultadoExecucao
from benchmark.services import dados_grafico, iniciar_execucao_assincrona, medias_por_combinacao, _filtrar_outliers


def _calcular_ic95(valores):
    """Calcula o intervalo de confiança de 95% para a média de uma amostra.

    Retorna (lower, upper) arredondados com 3 casas decimais.
    Usa Z=2 (aproximação normal), alinhado com analisar_resultados_estatistico.py.
    """
    n = len(valores)
    if n < 2:
        media = valores[0] if n == 1 else 0
        return (round(media, 3), round(media, 3))
    media = statistics.fmean(valores)
    s = statistics.stdev(valores)
    z_crit = 2.0
    erro_padrao = s / (n ** 0.5)
    margem = z_crit * erro_padrao
    return (round(media - margem, 3), round(media + margem, 3))


def pagina_inicial(request):
    config = BenchmarkConfig.load()
    readonly = config.modo_apenas_leitura

    if request.method == 'POST':
        if readonly:
            form = ConfiguracaoBenchmarkForm()
            form.add_error(None, 'O sistema esta em modo apenas leitura. Nao e possivel iniciar novas execucoes.')
            return render(request, 'benchmark/configuracao.html', {'form': form, 'readonly': readonly})
        form = ConfiguracaoBenchmarkForm(request.POST)
        if form.is_valid():
            vetor_str = form.cleaned_data['vetor_personalizado']
            if vetor_str and vetor_str.strip():
                vetor_parsed = [int(x.strip()) for x in vetor_str.split(',') if x.strip()]
                tamanhos = [len(vetor_parsed)]
            elif form.cleaned_data['tamanho'] == 'outro':
                tamanhos = [form.cleaned_data['tamanho_personalizado']]
            else:
                tamanhos = [int(form.cleaned_data['tamanho'])]

            execucao = ExecucaoBenchmark.objects.create(
                nome=form.cleaned_data['nome'] or f'{form.cleaned_data["algoritmo"]} :: Tamanho {tamanhos[0]}',
                algoritmos=[form.cleaned_data['algoritmo']],
                condicoes=form.cleaned_data['condicoes'],
                tamanhos=tamanhos,
                repeticoes=form.cleaned_data['repeticoes'],
                vetor_personalizado=form.cleaned_data['vetor_personalizado'],
                permitir_repetidos=form.cleaned_data.get('permitir_repetidos', False),
            )
            iniciar_execucao_assincrona(execucao.id)
            return redirect('benchmark:acompanhar_execucao', execucao_id=execucao.id)
    else:
        form = ConfiguracaoBenchmarkForm()
    return render(request, 'benchmark/configuracao.html', {'form': form, 'readonly': readonly})


def listar_execucoes(request):
    config = BenchmarkConfig.load()
    readonly = config.modo_apenas_leitura
    execucoes = ExecucaoBenchmark.objects.all().order_by('-criado_em')
    return render(request, 'benchmark/lista_execucoes.html', {'execucoes': execucoes, 'readonly': readonly})


@require_POST
def excluir_execucao(request, execucao_id):
    config = BenchmarkConfig.load()
    if config.modo_apenas_leitura:
        return redirect('benchmark:listar_execucoes')
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)
    execucao.delete()
    return redirect('benchmark:listar_execucoes')


@require_POST
def excluir_multiplas_execucoes(request):
    config = BenchmarkConfig.load()
    if config.modo_apenas_leitura:
        return redirect('benchmark:listar_execucoes')
    ids = request.POST.getlist('execucoes')
    if ids:
        ExecucaoBenchmark.objects.filter(id__in=ids).delete()
    return redirect('benchmark:listar_execucoes')


def acompanhar_execucao(request, execucao_id):
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)
    return render(request, 'benchmark/execucao.html', {'execucao': execucao})


def status_execucao(request, execucao_id):
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)
    return JsonResponse(
        {
            'status': execucao.status,
            'progresso_texto': execucao.progresso_texto,
            'url_resultados': reverse('benchmark:resultados_execucao', kwargs={'execucao_id': execucao.id}),
        }
    )


def resultados_execucao(request, execucao_id):
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)
    resultados = ResultadoExecucao.objects.filter(execucao=execucao)
    medias, dados_grafico = medias_por_combinacao(execucao)
    contexto = {
        'execucao': execucao,
        'resultados': resultados,
        'medias': medias,
        'dados_grafico_json': dados_grafico,
    }
    return render(request, 'benchmark/resultados.html', contexto)


def comparar_algoritmos(request):

    resultados = ResultadoExecucao.objects.select_related('execucao').all().order_by('algoritmo', 'condicao', 'tamanho')

    grupos = defaultdict(list)

    for r in resultados:
        chave = (r.algoritmo, r.condicao, r.tamanho, r.execucao.repeticoes, r.execucao.permitir_repetidos)
        grupos[chave].append(r)

    medias = []
    for (algoritmo, condicao, tamanho, _rep, _permitir_rep), itens in grupos.items():
        tempos = [r.tempo_ms for r in itens]
        comparacoes = [r.comparacoes for r in itens]

        media_tempo = round(sum(tempos) / len(tempos), 3)
        media_comp = round(sum(comparacoes) / len(comparacoes), 3)

        desvio_tempo = round(statistics.stdev(tempos), 3) if len(tempos) > 1 else 0
        desvio_comp = round(statistics.stdev(comparacoes), 3) if len(comparacoes) > 1 else 0

        # ---- Versao sem outliers (filtrada) ----
        tempos_filtrados, _, qtd_out_tempo = _filtrar_outliers(tempos)
        comps_filtrados, _, qtd_out_comp = _filtrar_outliers(comparacoes)

        if qtd_out_tempo > 0 and len(tempos_filtrados) >= 2:
            media_tempo_filt = round(sum(tempos_filtrados) / len(tempos_filtrados), 3)
            desvio_tempo_filt = round(statistics.stdev(tempos_filtrados), 3)
        else:
            media_tempo_filt = media_tempo
            desvio_tempo_filt = desvio_tempo
            qtd_out_tempo = 0

        if qtd_out_comp > 0 and len(comps_filtrados) >= 2:
            media_comp_filt = round(sum(comps_filtrados) / len(comps_filtrados), 3)
            desvio_comp_filt = round(statistics.stdev(comps_filtrados), 3)
        else:
            media_comp_filt = media_comp
            desvio_comp_filt = desvio_comp
            qtd_out_comp = 0

        n_original = len(itens)
        n_filtrado_tempo = len(tempos_filtrados) if qtd_out_tempo > 0 else n_original
        n_filtrado_comp = len(comps_filtrados) if qtd_out_comp > 0 else n_original

        # IC 95% para tempos e comparacoes (original e filtrado)
        ic95_tempo_lower, ic95_tempo_upper = _calcular_ic95(tempos)
        ic95_comp_lower, ic95_comp_upper = _calcular_ic95(comparacoes)

        tempos_para_ic95 = tempos_filtrados if qtd_out_tempo > 0 and len(tempos_filtrados) >= 2 else tempos
        comps_para_ic95 = comps_filtrados if qtd_out_comp > 0 and len(comps_filtrados) >= 2 else comparacoes
        ic95_tempo_filt_lower, ic95_tempo_filt_upper = _calcular_ic95(tempos_para_ic95)
        ic95_comp_filt_lower, ic95_comp_filt_upper = _calcular_ic95(comps_para_ic95)

        amostra = itens[0]
        permitir_repetidos = amostra.execucao.permitir_repetidos
        repeticoes = amostra.execucao.repeticoes

        medias.append({
            'algoritmo': algoritmo,
            'condicao': condicao,
            'tamanho': tamanho,
            'repeticoes': repeticoes,
            'permitir_repetidos': permitir_repetidos,
            # Original
            'media_tempo_ms': media_tempo,
            'desvio_tempo_ms': desvio_tempo,
            'ic95_tempo_lower': ic95_tempo_lower,
            'ic95_tempo_upper': ic95_tempo_upper,
            'media_comparacoes': media_comp,
            'desvio_comparacoes': desvio_comp,
            'ic95_comp_lower': ic95_comp_lower,
            'ic95_comp_upper': ic95_comp_upper,
            # Filtrado (sem outliers)
            'media_tempo_ms_filt': media_tempo_filt,
            'desvio_tempo_ms_filt': desvio_tempo_filt,
            'ic95_tempo_filt_lower': ic95_tempo_filt_lower,
            'ic95_tempo_filt_upper': ic95_tempo_filt_upper,
            'n_filtrado_tempo': n_filtrado_tempo,
            'removeu_outliers_tempo': qtd_out_tempo > 0,
            'media_comparacoes_filt': media_comp_filt,
            'desvio_comparacoes_filt': desvio_comp_filt,
            'ic95_comp_filt_lower': ic95_comp_filt_lower,
            'ic95_comp_filt_upper': ic95_comp_filt_upper,
            'n_filtrado_comp': n_filtrado_comp,
            'removeu_outliers_comp': qtd_out_comp > 0,
        })

    repeticoes_disponiveis = sorted(set(m['repeticoes'] for m in medias))

    return render(request, 'benchmark/comparar_algoritmos.html', {
        'medias_json': medias,
        'repeticoes_disponiveis': repeticoes_disponiveis,
    })
