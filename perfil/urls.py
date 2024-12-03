from django.urls import path
from .views.perfil import mostrar_perfil

app_name = 'perfil'  # Añade esta línea

urlpatterns = [
    path('mi-perfil/', mostrar_perfil, name='mi_perfil'),
]
