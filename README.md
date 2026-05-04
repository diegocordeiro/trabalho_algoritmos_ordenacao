# Parte I - Benchmark de Ordenação (PAA)

Projeto Django para execução e comparação de algoritmos de ordenação.

## Requisitos

- Python 3.13+
- Django 5.2.2

## Como rodar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Abra: `http://127.0.0.1:8000/`

## Fila no banco + worker serial (sem threading)

Em outro terminal, rode o worker único:

```bash
.venv/bin/python manage.py worker_benchmark
```

Esse worker processa execuções com `status=pendente` em ordem de criação, uma por vez.

## Execução por linha de comando (demonstração)

```bash
.venv/bin/python manage.py executar_parte1  --algoritmos mergesort --tamanhos 200000 --repeticoes 3 --nome Teste
```

## Módulos

- `ordenacao`: algoritmos de ordenação
- `benchmark`: configuração, execução assíncrona e persistência
- `relatorios`: exportação CSV 
