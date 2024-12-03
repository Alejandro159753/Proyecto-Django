# perfil/urls.py

from django.urls import path
from .views.perfil import mostrar_perfil  # Cambia esto si el archivo tiene otro nombre o ubicación
from .views.perfil import editar_perfil

app_name = 'perfil'

urlpatterns = [
    path('', mostrar_perfil, name='mi_perfil'),
    path('editar/', editar_perfil, name='editar_perfil'),
]
