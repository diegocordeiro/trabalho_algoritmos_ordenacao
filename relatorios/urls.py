from django.urls import path

from relatorios import views

app_name = 'relatorios'

urlpatterns = [
    path('execucao/<int:execucao_id>/csv/', views.exportar_csv, name='exportar_csv'),
]
