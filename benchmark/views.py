from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Avg

from benchmark.forms import ConfiguracaoBenchmarkForm
from benchmark.models import ExecucaoBenchmark, ResultadoExecucao
from benchmark.services import dados_grafico, iniciar_execucao_assincrona, medias_por_combinacao


def pagina_inicial(request):
    if request.method == 'POST':
        form = ConfiguracaoBenchmarkForm(request.POST)
        if form.is_valid():
            execucao = ExecucaoBenchmark.objects.create(
                nome=form.cleaned_data['nome'] or 'Execucao Parte I',
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
    medias = medias_por_combinacao(execucao)
    contexto = {
        'execucao': execucao,
        'resultados': resultados,
        'medias': medias,
        'dados_grafico_json': dados_grafico(execucao),
    }
    return render(request, 'benchmark/resultados.html', contexto)


def comparar_algoritmos(request):
    resultados = ResultadoExecucao.objects.all().order_by('algoritmo', 'condicao', 'tamanho')

    medias = (
        resultados
        .values('algoritmo', 'condicao', 'tamanho')
        .annotate(
            media_tempo_ms=Avg('tempo_ms'),
            media_comparacoes=Avg('comparacoes')
        )
        .order_by('algoritmo', 'condicao', 'tamanho')
    )

    return render(request, 'benchmark/comparar_algoritmos.html', {
        'medias_json': list(medias)
    })
