from django.urls import path

from benchmark import views

app_name = 'benchmark'

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),
    path('execucoes/', views.listar_execucoes, name='listar_execucoes'),
    path('execucao/<int:execucao_id>/excluir/', views.excluir_execucao, name='excluir_execucao'),
    path('execucao/<int:execucao_id>/', views.acompanhar_execucao, name='acompanhar_execucao'),
    path('execucao/<int:execucao_id>/status/', views.status_execucao, name='status_execucao'),
    path('execucao/<int:execucao_id>/resultados/', views.resultados_execucao, name='resultados_execucao'),
    path('comparar/', views.comparar_algoritmos, name='comparar_algoritmos'),
]
