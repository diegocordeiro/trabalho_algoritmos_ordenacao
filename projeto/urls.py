from django.urls import include, path

urlpatterns = [
    path('', include('benchmark.urls')),
    path('relatorios/', include('relatorios.urls')),
]
