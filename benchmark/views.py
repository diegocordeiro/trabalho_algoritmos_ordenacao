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
from benchmark.services import dados_grafico, iniciar_execucao_assincrona, medias_por_combinacao


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

    resultados = ResultadoExecucao.objects.all().order_by('algoritmo', 'condicao', 'tamanho')

    grupos = defaultdict(list)

    for r in resultados:
        chave = (r.algoritmo, r.condicao, r.tamanho)
        grupos[chave].append(r)

    medias = []
    for (algoritmo, condicao, tamanho), itens in grupos.items():
        tempos = [r.tempo_ms for r in itens]
        comparacoes = [r.comparacoes for r in itens]

        media_tempo = round(sum(tempos) / len(tempos), 2)
        media_comp = round(sum(comparacoes) / len(comparacoes), 2)

        desvio_tempo = round(statistics.stdev(tempos), 2) if len(tempos) > 1 else 0
        desvio_comp = round(statistics.stdev(comparacoes), 2) if len(comparacoes) > 1 else 0

        cv_tempo = round((desvio_tempo / media_tempo * 100), 2) if media_tempo > 0 else 0
        cv_comp = round((desvio_comp / media_comp * 100), 2) if media_comp > 0 else 0

        if cv_tempo < 5:
            classe_cv_tempo = 'muito estável'
        elif cv_tempo <= 15:
            classe_cv_tempo = 'aceitável'
        else:
            classe_cv_tempo = 'instável'

        if cv_comp < 5:
            classe_cv_comp = 'muito estável'
        elif cv_comp <= 15:
            classe_cv_comp = 'aceitável'
        else:
            classe_cv_comp = 'instável'

        medias.append({
            'algoritmo': algoritmo,
            'condicao': condicao,
            'tamanho': tamanho,
            'media_tempo_ms': media_tempo,
            'desvio_tempo_ms': desvio_tempo,
            'cv_tempo_pct': cv_tempo,
            'classe_cv_tempo': classe_cv_tempo,
            'media_comparacoes': media_comp,
            'desvio_comparacoes': desvio_comp,
            'cv_comparacoes_pct': cv_comp,
            'classe_cv_comparacoes': classe_cv_comp,
        })

    return render(request, 'benchmark/comparar_algoritmos.html', {
        'medias_json': medias
    })
