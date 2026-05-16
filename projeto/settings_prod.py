"""
Settings de producao para deploy em Docker.
Herda do settings.py e sobrescreve configuracoes para producao.
"""
import os
from pathlib import Path

# Herda tudo do settings base
from projeto.settings import *

# ============================================================
# SEGURANCA
# ============================================================
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'professordiegocordeiro.com.br,localhost,127.0.0.1'
).split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://professordiegocordeiro.com.br',
    'http://professordiegocordeiro.com.br',
]

# ============================================================
# BANCO DE DADOS — SQLite com volume persistente
# ============================================================
# O caminho /data/ sera montado como volume para persistir o db.sqlite3
DB_DIR = os.environ.get('DB_DIR', '/data')
os.makedirs(DB_DIR, exist_ok=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_DIR, 'db.sqlite3'),
    }
}

# ============================================================
# ARQUIVOS ESTATICOS E MEDIA
# ============================================================
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = '/comparacao_algoritmos/static/'

MEDIA_ROOT = '/app/media'
MEDIA_URL = '/comparacao_algoritmos/media/'

# ============================================================
# PREFIXO DE PATH (subdiretório)
# ============================================================
# Como a app roda sob /comparacao_algoritmos/, definimos o prefixo
FORCE_SCRIPT_NAME = '/comparacao_algoritmos'

# Configuracao para o nginx passar o header SCRIPT_NAME
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============================================================
# LOGGING
# ============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}