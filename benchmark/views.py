import statistics
from collections import defaultdict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Avg, FloatField
from django.db.models.functions import Round, Cast

from benchmark.forms import ConfiguracaoBenchmarkForm
from benchmark.models import ExecucaoBenchmark, ResultadoExecucao
from benchmark.services import dados_grafico, iniciar_execucao_assincrona, medias_por_combinacao, _filtrar_outliers


def pagina_inicial(request):
    if request.method == 'POST':
        form = ConfiguracaoBenchmarkForm(request.POST)
        if form.is_valid():
            execucao = ExecucaoBenchmark.objects.create(
                nome=form.cleaned_data['nome'] or f'{form.cleaned_data["algoritmo"]} :: Tamanho {form.cleaned_data["tamanho"]}',
                algoritmos=[form.cleaned_data['algoritmo']],
                condicoes=form.cleaned_data['condicoes'],
                tamanhos=[int(form.cleaned_data['tamanho'])],
                repeticoes=form.cleaned_data['repeticoes'],
                vetor_personalizado=form.cleaned_data['vetor_personalizado'],
                permitir_repetidos=form.cleaned_data.get('permitir_repetidos', False),
            )
            iniciar_execucao_assincrona(execucao.id)
            return redirect('benchmark:acompanhar_execucao', execucao_id=execucao.id)
    else:
        form = ConfiguracaoBenchmarkForm()
    return render(request, 'benchmark/configuracao.html', {'form': form})


def listar_execucoes(request):
    execucoes = ExecucaoBenchmark.objects.all().order_by('-criado_em')
    return render(request, 'benchmark/lista_execucoes.html', {'execucoes': execucoes})


@require_POST
def excluir_execucao(request, execucao_id):
    execucao = get_object_or_404(ExecucaoBenchmark, id=execucao_id)
    execucao.delete()
    return redirect('benchmark:listar_execucoes')


@require_POST
def excluir_multiplas_execucoes(request):
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
        chave = (r.algoritmo, r.condicao, r.tamanho, r.execucao.repeticoes)
        grupos[chave].append(r)

    medias = []
    for (algoritmo, condicao, tamanho, _rep), itens in grupos.items():
        tempos = [r.tempo_ms for r in itens]
        comparacoes = [r.comparacoes for r in itens]

        media_tempo = round(sum(tempos) / len(tempos), 2)
        media_comp = round(sum(comparacoes) / len(comparacoes), 2)

        desvio_tempo = round(statistics.stdev(tempos), 2) if len(tempos) > 1 else 0
        desvio_comp = round(statistics.stdev(comparacoes), 2) if len(comparacoes) > 1 else 0

        cv_tempo = round((desvio_tempo / media_tempo * 100), 2) if media_tempo > 0 else 0
        cv_comp = round((desvio_comp / media_comp * 100), 2) if media_comp > 0 else 0

        if cv_tempo <= 10:
            classe_cv_tempo = 'Muito Baixa Variação'
        elif cv_tempo <= 20:
            classe_cv_tempo = 'Moderada Variação'
        elif cv_tempo <= 30:
            classe_cv_tempo = 'Alta Variação'
        else:
            classe_cv_tempo = 'Variação Muito Alta'

        if cv_comp <= 10:
            classe_cv_comp = 'Muito Baixa Variação'
        elif cv_comp <= 20:
            classe_cv_comp = 'Moderada Variação'
        elif cv_comp <= 30:
            classe_cv_comp = 'Alta Variação'
        else:
            classe_cv_comp = 'Variação Muito Alta'

        # ---- Versao sem outliers (filtrada) ----
        tempos_filtrados, removeu_tempo = _filtrar_outliers(tempos)
        comps_filtrados, removeu_comp = _filtrar_outliers(comparacoes)

        if removeu_tempo and len(tempos_filtrados) >= 2:
            media_tempo_filt = round(sum(tempos_filtrados) / len(tempos_filtrados), 2)
            desvio_tempo_filt = round(statistics.stdev(tempos_filtrados), 2)
            cv_tempo_filt = round((desvio_tempo_filt / media_tempo_filt * 100), 2) if media_tempo_filt > 0 else 0
            classe_cv_tempo_filt = (
                'Muito Baixa Variação' if cv_tempo_filt <= 10 else
                'Moderada Variação' if cv_tempo_filt <= 20 else
                'Alta Variação' if cv_tempo_filt <= 30 else
                'Variação Muito Alta'
            )
        else:
            media_tempo_filt = media_tempo
            desvio_tempo_filt = desvio_tempo
            cv_tempo_filt = cv_tempo
            classe_cv_tempo_filt = classe_cv_tempo
            removeu_tempo = False

        if removeu_comp and len(comps_filtrados) >= 2:
            media_comp_filt = round(sum(comps_filtrados) / len(comps_filtrados), 2)
            desvio_comp_filt = round(statistics.stdev(comps_filtrados), 2)
            cv_comp_filt = round((desvio_comp_filt / media_comp_filt * 100), 2) if media_comp_filt > 0 else 0
            classe_cv_comp_filt = (
                'Muito Baixa Variação' if cv_comp_filt <= 10 else
                'Moderada Variação' if cv_comp_filt <= 20 else
                'Alta Variação' if cv_comp_filt <= 30 else
                'Variação Muito Alta'
            )
        else:
            media_comp_filt = media_comp
            desvio_comp_filt = desvio_comp
            cv_comp_filt = cv_comp
            classe_cv_comp_filt = classe_cv_comp
            removeu_comp = False

        n_original = len(itens)
        n_filtrado_tempo = len(tempos_filtrados) if removeu_tempo else n_original
        n_filtrado_comp = len(comps_filtrados) if removeu_comp else n_original

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
            'cv_tempo_pct': cv_tempo,
            'classe_cv_tempo': classe_cv_tempo,
            'media_comparacoes': media_comp,
            'desvio_comparacoes': desvio_comp,
            'cv_comparacoes_pct': cv_comp,
            'classe_cv_comparacoes': classe_cv_comp,
            # Filtrado (sem outliers)
            'media_tempo_ms_filt': media_tempo_filt,
            'desvio_tempo_ms_filt': desvio_tempo_filt,
            'cv_tempo_pct_filt': cv_tempo_filt,
            'classe_cv_tempo_filt': classe_cv_tempo_filt,
            'n_filtrado_tempo': n_filtrado_tempo,
            'removeu_outliers_tempo': removeu_tempo,
            'media_comparacoes_filt': media_comp_filt,
            'desvio_comparacoes_filt': desvio_comp_filt,
            'cv_comparacoes_pct_filt': cv_comp_filt,
            'classe_cv_comparacoes_filt': classe_cv_comp_filt,
            'n_filtrado_comp': n_filtrado_comp,
            'removeu_outliers_comp': removeu_comp,
        })

    repeticoes_disponiveis = sorted(set(m['repeticoes'] for m in medias))

    return render(request, 'benchmark/comparar_algoritmos.html', {
        'medias_json': medias,
        'repeticoes_disponiveis': repeticoes_disponiveis,
    })
