FROM python:3.11-slim

WORKDIR /app

# Instalar dependências de sistema necessárias para compilar matplotlib/numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório de staticfiles
RUN mkdir -p /app/staticfiles

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Copiar entrypoint
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]