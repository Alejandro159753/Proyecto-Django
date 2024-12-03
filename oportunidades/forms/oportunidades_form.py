from django import forms

class OportunidadesForm(forms.Form):
    title = forms.CharField(
        max_length=200, 
        label='Título', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el título de la oportunidad'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Proporcione una descripción detallada de la oportunidad'}),
        label='Descripción'
    )
    key_words = forms.CharField(
        max_length=255, 
        required=False, 
        label='Palabras clave', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Palabras clave relacionadas con la oportunidad'})
    )
    resources = forms.CharField(
        max_length=255, 
        required=False, 
        label='Recursos', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recursos necesarios para la implementación'})
    )
    innovation_type = forms.CharField(
        max_length=50, 
        label='Tipo de Oportunidad', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escriba el tipo de oportunidad'})
    )
    created_by = forms.CharField(
        max_length=100, 
        label='Creado por', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escriba el usuario que creó esta oportunidad'})
    )
    file = forms.FileField(
        required=False, 
        label='Archivo', 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
