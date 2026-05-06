import random
import time
import statistics
from collections import defaultdict

from benchmark.models import ExecucaoBenchmark, ResultadoExecucao
from ordenacao.algoritmos import ALGORITMOS


def _gerar_vetor(condicao, tamanho):
    # Se a condicao for crescente, gera um vetor 1..n em ordem crescente.
    if condicao == 'crescente':
        return list(range(1, tamanho + 1))
    # Se a condicao for decrescente, gera um vetor n..1 em ordem decrescente.
    if condicao == 'decrescente':
        return list(range(tamanho, 0, -1))
    # Cria vetor base 1..n para caso aleatorio.
    vetor = list(range(1, tamanho + 1))
    # Embaralha o vetor para obter distribuicao aleatoria dos elementos.
    random.shuffle(vetor)
    # Retorna o vetor gerado conforme a condicao solicitada.
    return vetor


def _parse_vetor_personalizado(texto):
    # Se o texto vier vazio ou com apenas espacos, indica ausencia de vetor customizado.
    if not texto.strip():
        return None
    # Divide por virgula, remove espacos e converte cada token para inteiro.
    return [int(parte.strip()) for parte in texto.split(',') if parte.strip()]


def iniciar_execucao_assincrona(execucao_id):
    # Carrega a execucao para registrar que ela entrou na fila persistida no banco.
    execucao = ExecucaoBenchmark.objects.get(id=execucao_id)
    # Mantem status como pendente ate o worker externo processar.
    execucao.status = 'pendente'
    # Registra mensagem de aguardando fila para feedback na interface.
    execucao.progresso_texto = 'Aguardando processamento na fila...'
    # Persiste os campos de fila sem executar benchmark no processo web.
    execucao.save(update_fields=['status', 'progresso_texto', 'atualizado_em'])


def executar_benchmark(execucao_id):
    # Carrega a execucao no banco a partir do id recebido.
    execucao = ExecucaoBenchmark.objects.get(id=execucao_id)
    # Marca status como executando antes de iniciar os loops.
    execucao.status = 'executando'
    # Define mensagem inicial de progresso.
    execucao.progresso_texto = 'Iniciando benchmark...'
    # Persiste status e progresso iniciais no banco.
    execucao.save(update_fields=['status', 'progresso_texto', 'atualizado_em'])

    try:
        # Faz parse do vetor personalizado informado pelo usuario, se existir.
        vetor_base_personalizado = _parse_vetor_personalizado(execucao.vetor_personalizado)
        # Calcula total de iteracoes combinando algoritmos x condicoes x tamanhos x repeticoes.
        total = len(execucao.algoritmos) * len(execucao.condicoes) * len(execucao.tamanhos) * execucao.repeticoes
        # Inicializa contador de progresso atual.
        passo = 0
        # Itera pelos algoritmos selecionados para esta execucao.
        for algoritmo_nome in execucao.algoritmos:
            # Resolve a funcao de ordenacao a partir do dicionario de algoritmos.
            funcao_ordenacao = ALGORITMOS[algoritmo_nome]
            # Itera pelas condicoes selecionadas.
            for condicao in execucao.condicoes:
                # Itera pelos tamanhos selecionados.
                for tamanho in execucao.tamanhos:
                    # Itera pelas repeticoes da combinacao atual.
                    for rodada in range(1, execucao.repeticoes + 1):
                        # Incrementa contador global de passos da execucao.
                        passo += 1
                        # Monta texto detalhado do passo atual para acompanhamento na interface.
                        execucao.progresso_texto = (
                            f'Executando {algoritmo_nome} | {condicao} | n={tamanho} | rodada {rodada}/{execucao.repeticoes} '
                            f'({passo}/{total})'
                        )
                        # Salva progresso corrente sem alterar outros campos.
                        execucao.save(update_fields=['progresso_texto', 'atualizado_em'])

                        # Se houver vetor personalizado, usa uma copia para evitar mutacao entre rodadas.
                        if vetor_base_personalizado is not None:
                            vetor_entrada = list(vetor_base_personalizado)
                        # Caso contrario, gera vetor conforme condicao e tamanho atuais.
                        else:
                            vetor_entrada = _gerar_vetor(condicao, int(tamanho))
                        # Captura timestamp de inicio em alta resolucao.
                        inicio = time.perf_counter()
                        # Executa algoritmo e captura quantidade de comparacoes retornada.
                        _, comparacoes = funcao_ordenacao(vetor_entrada)
                        # Captura timestamp de fim em alta resolucao.
                        fim = time.perf_counter()
                        # Persiste resultado unitario da rodada atual no banco.
                        ResultadoExecucao.objects.create(
                            execucao=execucao,
                            algoritmo=algoritmo_nome,
                            condicao=condicao,
                            tamanho=int(tamanho),
                            rodada=rodada,
                            tempo_ms=(fim - inicio) * 1000,
                            comparacoes=comparacoes,
                        )
        # Marca execucao como concluida apos finalizar todos os loops.
        execucao.status = 'concluido'
        # Atualiza mensagem final de sucesso.
        execucao.progresso_texto = 'Benchmark concluido com sucesso.'
        # Persiste status final de concluido.
        execucao.save(update_fields=['status', 'progresso_texto', 'atualizado_em'])
    # Captura qualquer excecao para registrar falha da execucao.
    except Exception as exc:
        # Marca status como erro quando ocorre excecao durante processamento.
        execucao.status = 'erro'
        # Registra mensagem de erro para exibicao na interface.
        execucao.progresso_texto = f'Erro durante a execucao: {exc}'
        # Persiste status e mensagem de erro no banco.
        execucao.save(update_fields=['status', 'progresso_texto', 'atualizado_em'])


def medias_por_combinacao(execucao):
    resultados = ResultadoExecucao.objects.filter(execucao=execucao)

    grupos = defaultdict(list)

    for r in resultados:
        chave = (r.algoritmo, r.condicao, r.tamanho)
        grupos[chave].append(r)

    medias = []
    dados = {}

    for (algoritmo, condicao, tamanho), itens in grupos.items():
        tempos = [r.tempo_ms for r in itens]
        comparacoes = [r.comparacoes for r in itens]

        media_tempo = sum(tempos) / len(tempos)
        media_comp = sum(comparacoes) / len(comparacoes)

        desvio_tempo = statistics.stdev(tempos) if len(tempos) > 1 else 0
        desvio_comp = statistics.stdev(comparacoes) if len(comparacoes) > 1 else 0

        medias.append({
            "algoritmo": algoritmo,
            "condicao": condicao,
            "tamanho": tamanho,
            "media_tempo_ms": media_tempo,
            "desvio_tempo_ms": desvio_tempo,
            "media_comparacoes": media_comp,
            "desvio_comparacoes": desvio_comp,
            "n": len(itens),
        })

        chave_nome = f"{algoritmo}-{condicao}"

        dados[chave_nome] = {
            "tamanhos": [tamanho],
            "tempos": [media_tempo],
            "desvio_tempo": [desvio_tempo],
            "comparacoes": [media_comp],
            "desvio_comparacoes": [desvio_comp],
        }

    return medias, dados


def dados_grafico(execucao):
    # Obtem medias agregadas para montar a estrutura de series dos graficos.
    medias = medias_por_combinacao(execucao)
    # Inicializa estrutura final no formato esperado pelo frontend.
    estrutura = {}
    # Itera por cada linha agregada para preencher series.
    for item in medias:
        # Define chave da serie no formato "algoritmo (condicao)".
        chave = f"{item['algoritmo']} ({item['condicao']})"
        # Garante que a chave exista com listas vazias antes de inserir dados.
        estrutura.setdefault(chave, {'tamanhos': [], 'tempos': [], 'comparacoes': []})
        # Adiciona tamanho na serie correspondente.
        estrutura[chave]['tamanhos'].append(item['tamanho'])
        # Adiciona tempo medio arredondado para exibicao.
        estrutura[chave]['tempos'].append(round(item['media_tempo_ms'], 4))
        # Adiciona comparacoes medias arredondadas para exibicao.
        estrutura[chave]['comparacoes'].append(round(item['media_comparacoes'], 2))
    # Retorna estrutura final para consumo dos graficos na view.
    return estrutura
