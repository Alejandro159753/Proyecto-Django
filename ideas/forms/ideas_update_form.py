from django import forms
import requests

# Función que hace la consulta a la API y obtiene los datos
def obtener_focos_innovacion():
    response = requests.get("http://190.217.58.246:5186/api/sgv/foco_innovacion")
    return [(foco['id_foco_innovacion'], foco['name']) for foco in response.json()]

def obtener_tipos_innovacion():
    response = requests.get("http://190.217.58.246:5186/api/sgv/tipo_innovacion")
    return [(tipo['id_tipo_innovacion'], tipo['name']) for tipo in response.json()]

class Ideas_update_Form(forms.Form):
    titulo = forms.CharField(
        max_length=255,
        required=True,
        label='Título',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el título de la idea'})
    )
    descripcion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Proporcione una descripción detallada de la idea'}),
        label='Descripción'
    )
    recursos_requeridos = forms.IntegerField(
        required=True,
        label='Recursos Requeridos',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad de recursos necesarios'})
    )
    palabras_claves = forms.CharField(
        max_length=255,
        required=True,
        label='Palabras Claves',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Palabras clave relacionadas con la idea'})
    )
    fecha_creacion = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Fecha de Creación'
    )
    archivo_multimedia = forms.FileField(
        required=False,
        label='Archivos Multimedia',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Sube un archivo multimedia'})
    )

    # Usando ChoiceField con los datos de la API
    id_foco_innovacion = forms.ChoiceField(
        choices=[(foco[0], foco[1]) for foco in obtener_focos_innovacion()],
        required=True,
        label='Foco de Innovación',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    id_tipo_innovacion = forms.ChoiceField(
        choices=[(tipo[0], tipo[1]) for tipo in obtener_tipos_innovacion()],
        required=True,
        label='Tipo de Innovación',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Campo para el mensaje del experto, visible solo si el usuario es experto
    mensaje_experto = forms.CharField(
        required=False,
        label='Mensaje del Experto',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Deja tu mensaje como experto aquí'}),
    )


