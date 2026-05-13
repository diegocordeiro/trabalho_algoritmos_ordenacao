# Implementação e Comparação de Algoritmos de Ordenação

- Projeto Django para execução e comparação de algoritmos de ordenação.
- Disciplina: Projeto e Análise de Algoritmos.
- Integrantes: Arthur Fernando Elvas Bohn, Diego Cordeiro de Oliveira e Keoma de Sousa Coelho.
- Orientador: Professor Dr. Guilherme Amaral Avelino.

## Requisitos

- Python 3.13+
- Django 5.2.2

## Como rodar (configuração de ambiente)

No terminal execute a sequencia a seguir:

**1. Clone o repositório:**
```bash
git clone https://github.com/diegocordeiro/trabalho_algoritmos_ordenacao.git
cd trabalho_algoritmos_ordenacao
```

**2. Instale o virtualenv** (caso o comando `python3 -m venv` não funcione):

```bash
# Ubuntu/Debian
sudo apt install python3-venv

# macOS (com Homebrew)
brew install python3
```

**3. Em seguida**, ainda dentro da pasta do projeto:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
```

## Execução por linha de comando

Para executar o benchmark com todos os algoritmos, 3 rodadas e tamanho 500, basta rodar o comando **sem parâmetros**:

```bash
.venv/bin/python manage.py executar_parte1
```

Isso executará todos os 5 algoritmos (`bublesort`, `insertionsort`, `mergesort`, `heap`, `quicksort`) nas 3 condições (`crescente`, `decrescente`, `aleatorio`) com vetores de tamanho 500 e 3 repetições cada de maneira sequêncial.

A saída é armazenada no banco de dados `db.sqlite3` e também em um arquivo CSV na pasta `resultados/` (`resultados/execucao_{id}.csv`).

### Parâmetros disponíveis

Caso queira customizar a execução, os seguintes parâmetros podem ser alterados:

| Parâmetro | Valor padrão | Descrição |
|---|---|---|
| `--algoritmos` | `bublesort,insertionsort,mergesort,heap,quicksort` | Algoritmos a executar, separados por vírgula |
| `--condicoes` | `crescente,decrescente,aleatorio` | Condições do vetor de entrada, separadas por vírgula |
| `--tamanhos` | `500` | Tamanhos dos vetores, separados por vírgula |
| `--repeticoes` | `3` | Número de repetições por combinação |
| `--nome` | `Execucao Parte I` | Nome descritivo da execução |
| `--permitir-repetidos` | `False` (flag) | Permite que os vetores gerados automaticamente (crescente, decrescente e aleatório) contenham números repetidos. Quando ausente, os vetores são gerados sem elementos repetidos. |
| `--vetor-personalizado` | (vazio) | Vetor personalizado com números separados por vírgula |

### Exemplo com parâmetros personalizados

```bash
.venv/bin/python manage.py executar_parte1 --algoritmos mergesort,quicksort --tamanhos 1000,5000 --repeticoes 5 --nome "Comparar Merge Sort com Quick Sort"
```

## Execução via interface web

Para utilizar a interface web, suba o servidor:

```bash
.venv/bin/python manage.py runserver
```

Abra: `http://127.0.0.1:8000/`

## Fila no banco + worker serial

Em outro terminal, rode o worker único:

```bash
.venv/bin/python manage.py worker_benchmark
```

Esse worker processa execuções com `status=pendente` em ordem de criação, uma por vez.

## Módulos

- **`ordenacao`**: Implementa os 5 algoritmos de ordenação clássicos — Bubble Sort, Insertion Sort, Merge Sort, Heap Sort e Quick Sort — conforme descritos no livro *Algoritmo Teoria e Prática* (Cormen et al., 2012, 3ª edição), um por arquivo como solicitado na especificação do problema. A pasta **`algoritmos`** armazena os arquivos individuais. Cada algoritmo retorna o vetor ordenado e a contagem de comparações realizadas durante a execução.

- **`benchmark`**: Responsável por orquestrar as execuções de benchmark. Permite configurar quais algoritmos, condições do vetor de entrada (crescente, decrescente, aleatório), tamanhos de entrada e número de repetições serão utilizados. A execução é gerenciada via fila no banco de dados com processamento por um worker serial (uma execução por vez). Após a conclusão, calcula métricas estatísticas (médias, desvio padrão, coeficiente de variação), aplica filtragem de outliers e prepara os dados para visualização em gráficos comparativos na interface web.

- **`relatorios`**: Responsável pela exportação dos resultados. Gera arquivos CSV com estatísticas filtradas (após remoção de outliers) contendo tempo médio, desvio padrão, coeficiente de variação, classe de variabilidade e contagem de comparações para cada combinação de algoritmo, condição e tamanho. Suporta exportação de uma única execução ou de múltiplas execuções selecionadas pelo usuário.
