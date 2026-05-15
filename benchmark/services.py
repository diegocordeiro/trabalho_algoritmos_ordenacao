import csv
import os
import random
import time
import statistics
import math
from collections import defaultdict

from django.conf import settings

from benchmark.models import ExecucaoBenchmark, ResultadoExecucao
from ordenacao.algoritmos import ALGORITMOS


def _filtrar_outliers(valores, limiar_cv=20, zscore_max=2.0):
    """
    Remove outliers de uma lista de valores com base no coeficiente de variacao.
    Se o CV for maior que o limiar (indicando instabilidade), remove valores
    cujo z-score absoluto exceda zscore_max.
    Retorna a lista filtrada e um booleano indicando se houve remocao.
    """
    if len(valores) < 3:
        return list(valores), False

    media = statistics.mean(valores)
    desvio = statistics.stdev(valores) if len(valores) > 1 else 0

    if media == 0 or desvio == 0:
        return list(valores), False

    cv = (desvio / media) * 100

    # So filtra se o CV indicar instabilidade
    if cv <= limiar_cv:
        return list(valores), False

    # Remove valores com z-score absoluto acima do limite
    filtrados = [v for v in valores if abs((v - media) / desvio) <= zscore_max]

    # Se removeu todos ou quase todos, retorna os originais
    if len(filtrados) < 2:
        return list(valores), False

    return filtrados, len(filtrados) < len(valores)


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


def _gerar_vetor_com_repeticao(condicao, tamanho):
    # Gera k amostras com reposicao do intervalo 1..tamanho, onde k = tamanho.
    if condicao == 'crescente':
        vetor = random.choices(range(1, tamanho + 1), k=tamanho)
        vetor.sort()
        return vetor
    if condicao == 'decrescente':
        vetor = random.choices(range(1, tamanho + 1), k=tamanho)
        vetor.sort(reverse=True)
        return vetor
    # Para aleatorio, retorna amostras com reposicao na ordem natural do choices.
    return random.choices(range(1, tamanho + 1), k=tamanho)


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
                        # Determina o tamanho efetivo: len do vetor personalizado ou o tamanho da iteracao.
                        tamanho_efetivo = len(vetor_base_personalizado) if vetor_base_personalizado is not None else int(tamanho)
                        # Monta texto detalhado do passo atual para acompanhamento na interface.
                        execucao.progresso_texto = (
                            f'Executando {algoritmo_nome} | {condicao} | n={tamanho_efetivo} | rodada {rodada}/{execucao.repeticoes} '
                            f'({passo}/{total})'
                        )
                        # Salva progresso corrente sem alterar outros campos.
                        execucao.save(update_fields=['progresso_texto', 'atualizado_em'])

                        # Se houver vetor personalizado, usa uma copia para evitar mutacao entre rodadas.
                        if vetor_base_personalizado is not None:
                            vetor_entrada = list(vetor_base_personalizado)
                        # Caso contrario, gera vetor conforme condicao, tamanho e configuracao de repeticao.
                        elif execucao.permitir_repetidos:
                            vetor_entrada = _gerar_vetor_com_repeticao(condicao, int(tamanho))
                        else:
                            vetor_entrada = _gerar_vetor(condicao, int(tamanho))
                        # Captura timestamp de inicio em alta resolucao.
                        inicio = time.perf_counter()
                        # Executa algoritmo e captura quantidade de comparacoes retornada.
                        # Todos os algoritmos possuem a mesma assinatura.
                        # O hibrido_final detecta automaticamente se ha elementos
                        # repetidos via set() na varredura O(n), sem precisar de flag.
                        _, comparacoes = funcao_ordenacao(vetor_entrada)
                        # Captura timestamp de fim em alta resolucao.
                        fim = time.perf_counter()
                        # Persiste resultado unitario da rodada atual no banco.
                        ResultadoExecucao.objects.create(
                            execucao=execucao,
                            algoritmo=algoritmo_nome,
                            condicao=condicao,
                            tamanho=tamanho_efetivo,
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

        # ---- Versao original (com todos os valores) ----
        media_tempo = sum(tempos) / len(tempos)
        media_comp = sum(comparacoes) / len(comparacoes)

        desvio_tempo = statistics.stdev(tempos) if len(tempos) > 1 else 0
        desvio_comp = statistics.stdev(comparacoes) if len(comparacoes) > 1 else 0
        cv_tempo = (desvio_tempo / media_tempo * 100) if media_tempo > 0 else 0
        cv_comp = (desvio_comp / media_comp * 100) if media_comp > 0 else 0

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
            media_tempo_filt = sum(tempos_filtrados) / len(tempos_filtrados)
            desvio_tempo_filt = statistics.stdev(tempos_filtrados)
            cv_tempo_filt = (desvio_tempo_filt / media_tempo_filt * 100) if media_tempo_filt > 0 else 0
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
            media_comp_filt = sum(comps_filtrados) / len(comps_filtrados)
            desvio_comp_filt = statistics.stdev(comps_filtrados)
            cv_comp_filt = (desvio_comp_filt / media_comp_filt * 100) if media_comp_filt > 0 else 0
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

        medias.append({
            "algoritmo": algoritmo,
            "condicao": condicao,
            "tamanho": tamanho,
            # Original
            "media_tempo_ms": media_tempo,
            "desvio_tempo_ms": desvio_tempo,
            "cv_tempo_pct": cv_tempo,
            "classe_cv_tempo": classe_cv_tempo,
            "media_comparacoes": media_comp,
            "desvio_comparacoes": desvio_comp,
            "cv_comparacoes_pct": cv_comp,
            "classe_cv_comparacoes": classe_cv_comp,
            "n": n_original,
            # Filtrado (sem outliers)
            "media_tempo_ms_filt": media_tempo_filt,
            "desvio_tempo_ms_filt": desvio_tempo_filt,
            "cv_tempo_pct_filt": cv_tempo_filt,
            "classe_cv_tempo_filt": classe_cv_tempo_filt,
            "n_filtrado_tempo": n_filtrado_tempo,
            "removeu_outliers_tempo": removeu_tempo,
            "media_comparacoes_filt": media_comp_filt,
            "desvio_comparacoes_filt": desvio_comp_filt,
            "cv_comparacoes_pct_filt": cv_comp_filt,
            "classe_cv_comparacoes_filt": classe_cv_comp_filt,
            "n_filtrado_comp": n_filtrado_comp,
            "removeu_outliers_comp": removeu_comp,
        })

        chave_nome = f"{algoritmo}-{condicao}"

        if chave_nome not in dados:
            dados[chave_nome] = {
                "tamanhos": [],
                "tempos": [],
                "desvio_tempo": [],
                "cv_tempo_pct": [],
                "classe_cv_tempo": [],
                "comparacoes": [],
                "desvio_comparacoes": [],
                "cv_comparacoes_pct": [],
                "classe_cv_comparacoes": [],
                # Filtrado (sem outliers)
                "tempos_filt": [],
                "desvio_tempo_filt": [],
                "comparacoes_filt": [],
                "desvio_comparacoes_filt": [],
            }
        dados[chave_nome]["tamanhos"].append(tamanho)
        dados[chave_nome]["tempos"].append(media_tempo)
        dados[chave_nome]["desvio_tempo"].append(desvio_tempo)
        dados[chave_nome]["cv_tempo_pct"].append(cv_tempo)
        dados[chave_nome]["classe_cv_tempo"].append(classe_cv_tempo)
        dados[chave_nome]["comparacoes"].append(media_comp)
        dados[chave_nome]["desvio_comparacoes"].append(desvio_comp)
        dados[chave_nome]["cv_comparacoes_pct"].append(cv_comp)
        dados[chave_nome]["classe_cv_comparacoes"].append(classe_cv_comp)
        # Filtrado (sem outliers)
        dados[chave_nome]["tempos_filt"].append(media_tempo_filt)
        dados[chave_nome]["desvio_tempo_filt"].append(desvio_tempo_filt)
        dados[chave_nome]["comparacoes_filt"].append(media_comp_filt)
        dados[chave_nome]["desvio_comparacoes_filt"].append(desvio_comp_filt)

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
        if chave not in estrutura:
            estrutura[chave] = {
                'tamanhos': [],
                'tempos': [],
                'comparacoes': [],
                'desvio_tempo': [],
                'desvio_comparacoes': [],
                # Filtrado (sem outliers)
                'tempos_filt': [],
                'desvio_tempo_filt': [],
                'comparacoes_filt': [],
                'desvio_comparacoes_filt': [],
            }
        # Adiciona tamanho na serie correspondente.
        estrutura[chave]['tamanhos'].append(item['tamanho'])
        # Original
        estrutura[chave]['tempos'].append(round(item['media_tempo_ms'], 4))
        estrutura[chave]['desvio_tempo'].append(round(item['desvio_tempo_ms'], 4))
        estrutura[chave]['comparacoes'].append(round(item['media_comparacoes'], 2))
        estrutura[chave]['desvio_comparacoes'].append(round(item['desvio_comparacoes'], 2))
        # Filtrado (sem outliers)
        estrutura[chave]['tempos_filt'].append(round(item['media_tempo_ms_filt'], 4))
        estrutura[chave]['desvio_tempo_filt'].append(round(item['desvio_tempo_ms_filt'], 4))
        estrutura[chave]['comparacoes_filt'].append(round(item['media_comparacoes_filt'], 2))
        estrutura[chave]['desvio_comparacoes_filt'].append(round(item['desvio_comparacoes_filt'], 2))
    # Retorna estrutura final para consumo dos graficos na view.
    return estrutura


def gerar_csv_resultados_arquivo(execucao_id):
    """
    Gera um arquivo CSV com os dados detalhados da execucao
    (algoritmo, condicao, tamanho, rodada, tempo_ms, comparacoes)
    e salva na pasta resultados/.
    Inclui uma linha de MEDIA ao final de cada grupo (algoritmo + condicao + tamanho).
    Retorna o caminho do arquivo gerado.
    """
    resultados = ResultadoExecucao.objects.filter(execucao_id=execucao_id).order_by(
        'algoritmo', 'condicao', 'tamanho', 'rodada'
    )

    # Garante que o diretorio resultados/ existe
    base_dir = os.path.join(settings.BASE_DIR, 'resultados')
    os.makedirs(base_dir, exist_ok=True)

    nome_arquivo = f'execucao_{resultados.first().algoritmo}_{execucao_id}.csv'
    caminho_arquivo = os.path.join(base_dir, nome_arquivo)

    with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        cabecalho = ['algoritmo', 'condicao', 'tamanho', 'rodada', 'tempo_ms', 'comparacoes', 'permitir_repetidos']
        writer.writerow(cabecalho)

        grupo_atual = None
        tempos_grupo = []
        comps_grupo = []
        permitir_repetidos_valor = 'Nao'

        def _escrever_media():
            """Escreve a linha de media para o grupo acumulado."""
            media_tempo = sum(tempos_grupo) / len(tempos_grupo)
            media_comp = sum(comps_grupo) / len(comps_grupo)
            writer.writerow([
                grupo_atual[0],
                grupo_atual[1],
                grupo_atual[2],
                f'MEDIA (n={len(tempos_grupo)})',
                f'{media_tempo:.2f}',
                f'{media_comp:.2f}',
                permitir_repetidos_valor,
            ])

        for r in resultados:
            chave = (r.algoritmo, r.condicao, r.tamanho)

            # Se mudou o grupo, escreve a media do grupo anterior
            if grupo_atual is not None and chave != grupo_atual:
                _escrever_media()
                tempos_grupo = []
                comps_grupo = []

            grupo_atual = chave
            permitir_repetidos_valor = 'Sim' if r.execucao.permitir_repetidos else 'Nao'
            tempos_grupo.append(r.tempo_ms)
            comps_grupo.append(r.comparacoes)

            writer.writerow([
                r.algoritmo,
                r.condicao,
                r.tamanho,
                r.rodada,
                f'{r.tempo_ms:.2f}',
                f'{r.comparacoes:.2f}',
                permitir_repetidos_valor,
            ])

        # Escreve a media do ultimo grupo
        if grupo_atual is not None and tempos_grupo:
            _escrever_media()

    return caminho_arquivo
