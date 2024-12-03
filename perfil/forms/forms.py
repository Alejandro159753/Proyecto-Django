# forms/forms.py
from django import forms

# Formulario para editar el perfil
class PerfilForm(forms.Form):
    # Datos del perfil
    nombre = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Nombre completo'}))
    direccion = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Dirección'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Descripción personal'}))

    # Fecha de nacimiento
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de nacimiento"
    )
    
    # Áreas de Expertise
    area_expertise = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Área de Expertise'}))

    # Información adicional
    info_adicional = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Información adicional'}))

    # Para validación, puedes agregar que los campos no pueden estar vacíos si lo consideras necesario
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        direccion = cleaned_data.get('direccion')
        descripcion = cleaned_data.get('descripcion')

        # Ejemplo de validación personalizada si algún campo está vacío
        if not nombre or not direccion or not descripcion:
            raise forms.ValidationError("Todos los campos son obligatorios")

        return cleaned_data
