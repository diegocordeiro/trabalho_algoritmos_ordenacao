from django.urls import path

from relatorios import views

app_name = 'relatorios'

urlpatterns = [
    path('relatorios/exportar/<int:execucao_id>/', views.exportar_csv, name='exportar_csv'),
    path('relatorios/exportar-selecionadas/', views.exportar_csv_selecionadas, name='exportar_csv_selecionadas'),
]
