from django.shortcuts import render, redirect, get_object_or_404
from oportunidades.models import APIClient
from django.contrib import messages
from oportunidades.forms.oportunidades_form import OportunidadesForm
import requests

def list_oportunidad(request):
    client = APIClient('oportunidades')
    oportunidades = client.get_data()
    return render(request, 'oportunidades/list.html', {'oportunidades': oportunidades})


def create_oportunidad(request):
    if request.method == 'POST':
        form = OportunidadesForm(request.POST, request.FILES)
        if form.is_valid():
            client = APIClient('oportunidades')
            try:
                response = client.insert_data(json_data=form.cleaned_data)
                messages.success(request, 'Oportunidad creada con éxito.')
                return redirect('list_oportunidades')
            except requests.exceptions.HTTPError as e:
                messages.error(request, f'Error al crear la oportunidad: {e}')
                print(f'Error al crear la oportunidad: {e}')  # Depuración
            except Exception as e:
                messages.error(request, f'Error inesperado: {e}')
                print(f'Error inesperado: {e}')  # Depuración
    else:
        form = OportunidadesForm()
    return render(request, 'oportunidades/create.html', {'form': form})


def update_oportunidad(request, pk):
    client = APIClient('oportunidades')
    oportunidad = client.get_data(where_condition=f"id = {pk}")
    if not oportunidad:
        return redirect('list_oportunidades')

    if request.method == 'POST':
        form = OportunidadesForm(request.POST, request.FILES)
        if form.is_valid():
            client.update_data(where_condition=f"id = {pk}", json_data=form.cleaned_data)
            messages.success(request, 'Oportunidad actualizada con éxito.')
            return redirect('list_oportunidades')
    else:
        form = OportunidadesForm(initial=oportunidad[0])

    return render(request, 'oportunidades/update.html', {'form': form})


def delete_oportunidad(request, pk):
    client = APIClient('oportunidades')
    oportunidad = client.get_data(where_condition=f"id = {pk}")
    if not oportunidad:
        return redirect('list_oportunidades')

    if request.method == 'POST':
        client.delete_data(where_condition=f"id = {pk}")
        messages.success(request, 'Oportunidad eliminada con éxito.')
        return redirect('list_oportunidades')

    return render(request, 'oportunidades/delete.html', {'oportunidad': oportunidad[0]})
