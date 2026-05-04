def ordenar_insercao(vetor):
    # Cria uma copia do vetor para preservar os dados originais.
    arr = list(vetor)
    # Inicializa o contador de comparacoes com zero.
    comparacoes = 0
    # Percorre o vetor da segunda posicao ate o final.
    for j in range(1, len(arr)):
        # Define a chave que sera inserida na porcao ordenada.
        chave = arr[j]
        # Define o indice do ultimo elemento da porcao ordenada.
        i = j - 1
        # Entra no laco enquanto existir elemento a comparar na esquerda.
        while i >= 0:
            # Conta a comparacao logica entre arr[i] e chave.
            comparacoes += 1
            # Verifica se o elemento atual e maior que a chave.
            if arr[i] > chave:
                # Desloca o elemento para a direita para abrir espaco.
                arr[i + 1] = arr[i]
                # Move o indice para a esquerda para continuar as comparacoes.
                i -= 1
            else:
                # Interrompe o laco quando a posicao correta da chave e encontrada.
                break
        # Insere a chave na posicao correta da porcao ordenada.
        arr[i + 1] = chave
    # Retorna o vetor ordenado e o total de comparacoes realizadas.
    return arr, comparacoes
