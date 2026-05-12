# Trabalho Prático de Projeto e Análise de Algoritmos: Implementação e Comparação de Algoritmos de Ordenação

Projeto Django para execução e comparação de algoritmos de ordenação.
Disciplina Projeto e Análise de Algorimos.
Integrantes: Arthur Fernando Elvas Bohn, Diego Cordeiro de Oliveira e Keoma de Sousa Coelho.
Orientador: Professor Dr. Guilherme Amaral Avelino.

## Requisitos

- Python 3.13+
- Django 5.2.2

## Como rodar (configuração de ambiente)

**Instale o virtualenv** (caso o comando `python3 -m venv` não funcione):

```bash
# Ubuntu/Debian
sudo apt install python3-venv

# macOS (com Homebrew)
brew install python3
```

Em seguida:

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

## Fila no banco + worker serial (sem threading)

Em outro terminal, rode o worker único:

```bash
.venv/bin/python manage.py worker_benchmark
```

Esse worker processa execuções com `status=pendente` em ordem de criação, uma por vez.

## Módulos

- `ordenacao`: algoritmos de ordenação
- `benchmark`: configuração, execução assíncrona e persistência
- `relatorios`: exportação CSV