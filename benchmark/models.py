from django.db import models


class BenchmarkConfig(models.Model):
    """Configuracao singleton do benchmark. Apenas uma instancia deve existir."""
    modo_apenas_leitura = models.BooleanField(
        default=False,
        verbose_name='Ativar modo apenas leitura',
        help_text='Quando ativado, bloqueia o envio de novas execucoes via formulario de configuracao.'
    )

    class Meta:
        verbose_name = 'Configuracao do Benchmark'
        verbose_name_plural = 'Configuracao do Benchmark'

    def save(self, *args, **kwargs):
        # Garante que exista apenas uma instancia (singleton)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Retorna a instancia unica de configuracao, criando-a se necessario."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Configuracao do Benchmark'


class ExecucaoBenchmark(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('executando', 'Executando'),
        ('concluido', 'Concluido'),
        ('erro', 'Erro'),
    ]

    nome = models.CharField(max_length=120, default='Execucao')
    algoritmos = models.JSONField(default=list)
    condicoes = models.JSONField(default=list)
    tamanhos = models.JSONField(default=list)
    repeticoes = models.PositiveIntegerField(default=3)
    vetor_personalizado = models.TextField(blank=True, default='')
    permitir_repetidos = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    progresso_texto = models.TextField(blank=True, default='Aguardando inicio...')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.nome} ({self.status})'


class ResultadoExecucao(models.Model):
    execucao = models.ForeignKey(ExecucaoBenchmark, on_delete=models.CASCADE, related_name='resultados')
    algoritmo = models.CharField(max_length=30)
    condicao = models.CharField(max_length=30)
    tamanho = models.PositiveIntegerField()
    rodada = models.PositiveIntegerField()
    tempo_ms = models.FloatField()
    comparacoes = models.PositiveBigIntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['algoritmo', 'condicao', 'tamanho', 'rodada']

    def __str__(self):
        return f'{self.algoritmo} {self.condicao} n={self.tamanho} r={self.rodada}'
