# Implementação e Comparação de Algoritmos de Ordenação

- Projeto Django para execução e comparação de algoritmos de ordenação.
- Disciplina: Projeto e Análise de Algoritmos.
- Integrantes: Arthur Fernando Elvas Bohn, Diego Cordeiro de Oliveira e Keoma de Sousa Coelho.
- Orientador: Professor Dr. Guilherme Amaral Avelino.

## Repositório GIT

- https://github.com/diegocordeiro/trabalho_algoritmos_ordenacao

## Requisitos

- Python 3.13+
- Django 5.2.2

## Como executar (configuração de ambiente)

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
.venv/bin/python manage.py executar_parte1 --algoritmos mergesort,quicksort --tamanhos 1000,5000 --repeticoes 5 --permitir-repetidos --nome "Comparar Merge Sort com Quick Sort"
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

- **`ordenacao`**: Implementa os 5 algoritmos de ordenação clássicos — Bubble Sort, Insertion Sort, Merge Sort, Heap Sort e Quick Sort — conforme descritos no livro *Algoritmo Teoria e Prática* (Cormen et al., 2012, 3ª edição), um por arquivo como solicitado na especificação do problema. A pasta **`algoritmos`** armazena os arquivos individuais. Cada algoritmo retorna o vetor ordenado e a contagem de comparações realizadas durante a execução. O arquivo **`algoritmos/__init__.py`** reúne as importações e exporta o dicionário `ALGORITMOS`, que mapeia o nome de cada algoritmo (`bublesort`, `insertionsort`, `mergesort`, `heap`, `quicksort`) para sua respectiva função de ordenação, permitindo que o módulo `benchmark` invoque qualquer algoritmo dinamicamente por nome.

- **`benchmark`**: Responsável por orquestrar as execuções de benchmark. Permite configurar quais algoritmos, condições do vetor de entrada (crescente, decrescente, aleatório), tamanhos de entrada e número de repetições serão utilizados. A execução é gerenciada via fila no banco de dados com processamento por um worker serial (uma execução por vez). Após a conclusão, calcula métricas estatísticas (médias, desvio padrão, coeficiente de variação), aplica filtragem de outliers e prepara os dados para visualização em gráficos comparativos na interface web. Seus principais arquivos são:
  - **`models.py`**: Define os modelos `ExecucaoBenchmark` (que armazena a configuração da execução, status — pendente, executando, concluído, erro — e progresso textual) e `ResultadoExecucao` (que persiste cada rodada individual com algoritmo, condição, tamanho, tempo em milissegundos e contagem de comparações).
  - **`services.py`**: Contém a lógica central do benchmark — geração de vetores (com ou sem repetição e vetores personalizados), loop de execução que itera sobre as combinações de algoritmo × condição × tamanho × repetição medindo tempo via `time.perf_counter()`, filtragem de outliers por z-score com base no coeficiente de variação, cálculo de médias, desvio padrão e coeficiente de variação por combinação, classificação de variabilidade (`Muito Baixa Variação` a `Variação Muito Alta`), preparação dos dados para gráficos e geração de arquivo CSV por execução na pasta `resultados/`.
  - **`forms.py`**: Define o formulário `ConfiguracaoBenchmarkForm`, que disponibiliza os campos de seleção de algoritmo, condições (checkbox múltiplo), tamanho (valores pré-definidos de 50 a 200.000 ou personalizado), número de repetições (mínimo 3), vetor personalizado (textarea) e flag para permitir números repetidos nos vetores gerados.
  - **`views.py`**: Implementa as views da interface web — página inicial com formulário de configuração e criação de execução, listagem e exclusão (individual ou múltipla) de execuções, acompanhamento em tempo real via polling AJAX (`status_execucao` retorna JSON com status e progresso), exibição de resultados com tabela de métricas e dados para gráficos, e comparação agregada entre todas as execuções com filtragem de outliers.
  - **`urls.py`**: Mapeia as rotas da interface web (`/`, `/execucoes/`, `/execucao/<id>/`, `/comparar/`, etc.) para as views correspondentes.
  - **`management/commands/executar_parte1.py`**: Comando Django (`manage.py executar_parte1`) que executa o benchmark diretamente via linha de comando com parâmetros customizáveis (`--algoritmos`, `--condicoes`, `--tamanhos`, `--repeticoes`, `--permitir-repetidos`, `--vetor-personalizado`), sem necessidade da interface web ou worker.
  - **`management/commands/worker_benchmark.py`**: Worker serial que consulta o banco em loop a cada 5 segundos por execuções com `status=pendente` e as processa uma por vez em ordem de criação, atualizando status e progresso durante a execução.

- **`relatorios`**: Responsável pela exportação dos resultados. Gera arquivos CSV com estatísticas filtradas (após remoção de outliers) contendo tempo médio, desvio padrão, coeficiente de variação, classe de variabilidade e contagem de comparações para cada combinação de algoritmo, condição e tamanho. Suporta exportação de uma única execução ou de múltiplas execuções selecionadas pelo usuário. Seus principais arquivos são:
  - **`views.py`**: Implementa as views de exportação — `exportar_csv` gera um arquivo CSV com métricas estatísticas filtradas (após remoção de outliers) para uma única execução; `exportar_csv_selecionadas` faz o mesmo para múltiplas execuções selecionadas via POST. Ambas utilizam `_gerar_csv_resultados`, que agrupa os resultados por algoritmo, condição e tamanho, aplica `_filtrar_outliers` nos tempos e comparações, calcula média, desvio padrão e coeficiente de variação pós-filtragem, classifica a variabilidade e escreve o CSV com cabeçalho padronizado.
  - **`urls.py`**: Mapeia as rotas de exportação — `/relatorios/exportar/<execucao_id>/` para exportar uma execução individual e `/relatorios/exportar-selecionadas/` para exportar múltiplas execuções selecionadas.
