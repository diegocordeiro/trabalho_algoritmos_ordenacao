import random
import threading
import time

from django.db.models import Avg

from benchmark.models import ExecucaoBenchmark, ResultadoExecucao
from ordenacao.algoritmos import ALGORITMOS


_lock_execucao = threading.Lock()
_execucao_threads = {}


def _gerar_vetor(condicao, tamanho):
    if condicao == 'crescente':
        return list(range(1, tamanho + 1))
    if condicao == 'decrescente':
        return list(range(tamanho, 0, -1))
    vetor = list(range(1, tamanho + 1))
    random.shuffle(vetor)
    return vetor


def _parse_vetor_personalizado(texto):
    if not texto.strip():
        return None
    return [int(parte.strip()) for parte in texto.split(',') if parte.strip()]


def iniciar_execucao_assincrona(execucao_id):
    with _lock_execucao:
        if execucao_id in _execucao_threads and _execucao_threads[execucao_id].is_alive():
            return
        thread = threading.Thread(target=executar_benchmark, args=(execucao_id,), daemon=True)
        _execucao_threads[execucao_id] = thread
        thread.start()


def executar_benchmark(execucao_id):
    execucao = ExecucaoBenchmark.objects.get(id=execucao_id)
    execucao.status = 'executando'
    execucao.progresso_texto = 'Iniciando benchmark...'
    execucao.save(update_fields=['status', 'progresso_texto', 'atualizado_em'])

    try:
        vetor_base_personalizado = _parse_vetor_personalizado(execucao.vetor_personalizado)
        total = len(execucao.algoritmos) * len(execucao.condicoes) * len(execucao.tamanhos) * execucao.repeticoes
        passo = 0
        for algoritmo_nome in execucao.algoritmos:
            funcao_ordenacao = ALGORITMOS[algoritmo_nome]
            for condicao in execucao.condicoes:
                for tamanho in execucao.tamanhos:
                    for rodada in range(1, execucao.repeticoes + 1):
                        passo += 1
                        execucao.progresso_texto = (
                            f'Executando {algoritmo_nome} | {condicao} | n={tamanho} | rodada {rodada}/{execucao.repeticoes} '
                            f'({passo}/{total})'
                        )
                        execucao.save(update_fields=['progresso_texto', 'atualizado_em'])

                        if vetor_base_personalizado is not None:
                            vetor_entrada = list(vetor_base_personalizado)
                        else:
                            vetor_entrada = _gerar_vetor(condicao, int(tamanho))
                        inicio = time.perf_counter()
                        _, comparacoes = funcao_ordenacao(vetor_entrada)
                        fim = time.perf_counter()
                        ResultadoExecucao.objects.create(
                            execucao=execucao,
                            algoritmo=algoritmo_nome,
                            condicao=condicao,
                            tamanho=int(tamanho),
                            rodada=rodada,
                            tempo_ms=(fim - inicio) * 1000,
                            comparacoes=comparacoes,
                        )
        execucao.status = 'concluido'
        execucao.progresso_texto = 'Benchmark concluido com sucesso.'
        execucao.save(update_fields=['status', 'progresso_texto', 'atualizado_em'])
    except Exception as exc:
        execucao.status = 'erro'
        execucao.progresso_texto = f'Erro durante a execucao: {exc}'
        execucao.save(update_fields=['status', 'progresso_texto', 'atualizado_em'])


def medias_por_combinacao(execucao):
    agrupado = (
        ResultadoExecucao.objects.filter(execucao=execucao)
        .values('algoritmo', 'condicao', 'tamanho')
        .annotate(media_tempo_ms=Avg('tempo_ms'), media_comparacoes=Avg('comparacoes'))
        .order_by('algoritmo', 'condicao', 'tamanho')
    )
    return list(agrupado)


def dados_grafico(execucao):
    medias = medias_por_combinacao(execucao)
    estrutura = {}
    for item in medias:
        chave = f"{item['algoritmo']} ({item['condicao']})"
        estrutura.setdefault(chave, {'tamanhos': [], 'tempos': [], 'comparacoes': []})
        estrutura[chave]['tamanhos'].append(item['tamanho'])
        estrutura[chave]['tempos'].append(round(item['media_tempo_ms'], 4))
        estrutura[chave]['comparacoes'].append(round(item['media_comparacoes'], 2))
    return estrutura
