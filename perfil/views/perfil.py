# perfil/views.py
from django.shortcuts import render
from oportunidades.models import APIClient

def mostrar_perfil(request):
    client = APIClient('perfil')
    perfil = client.get_data()
    return render(request, 'perfil/mi_perfil.html', {'perfil': perfil})

