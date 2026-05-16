from django.contrib import admin

from benchmark.models import BenchmarkConfig


@admin.register(BenchmarkConfig)
class BenchmarkConfigAdmin(admin.ModelAdmin):
    fields = ('modo_apenas_leitura',)

    def has_add_permission(self, request):
        # Bloqueia adicao de novas instancias (ja e singleton)
        return not BenchmarkConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Bloqueia exclusao da configuracao
        return False