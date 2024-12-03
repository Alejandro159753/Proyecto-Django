import os
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
import requests

# Clase para hacer peticiones a la API de Foco de Innovación
class FocoInnovacionAPI:
    @staticmethod
    def get_focos():
        api_url = "http://190.217.58.246:5186/api/sgv/foco_innovacion"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener focos: {e}")
            return []

# Clase para hacer peticiones a la API de Tipo de Innovación
class TipoInnovacionAPI:
    @staticmethod
    def get_tipo_innovacion():
        api_url = "http://190.217.58.246:5186/api/sgv/tipo_innovacion"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener tipos de innovación: {e}")
            return []

class APIClient:
    BASE_URL = "http://190.217.58.246:5186/api/SGV/procedures/execute"  # URL de la API

    def __init__(self, table_name):
        self.table_name = table_name

    def _make_request(self, procedure, where_condition=None, order_by=None, limit_clause=None, json_data=None, select_columns=None):
        url = self.BASE_URL
        payload = {
            "procedure": procedure,
            "parameters": {
                "table_name": self.table_name,
                "where_condition": where_condition,
                "order_by": order_by,
                "limit_clause": limit_clause,
                "json_data": json_data if json_data else {},
                "select_columns": select_columns
            }
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Lanza una excepción si la solicitud falla
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"Error HTTP: {err}")
            print("Detalles de la respuesta:", response.text)
            return None
        except Exception as e:
            print(f"Se produjo un error inesperado: {e}")
            return None
        


    def auto_update_data(self, where_condition=None, json_data=None):
        """Actualiza automáticamente los datos en la API solo si hay cambios"""
        if not where_condition or not json_data:
            return None

        # Paso 1: Obtener los datos actuales de la API
        current_data = self.get_data(where_condition=where_condition)
        if not current_data:
            return None
        
        current_data = current_data[0]  # Si solo hay un resultado, lo tomamos (suponiendo que es una lista de una sola idea)
        
        # Paso 2: Comparar los datos actuales con los nuevos datos
        updated_data = {}
        for key, value in json_data.items():
            # Si el valor actual es diferente al valor nuevo, lo actualizamos
            if current_data.get(key) != value:
                updated_data[key] = value
        
        # Paso 3: Si hay datos que han cambiado, realizar la actualización
        if updated_data:
            # Realizamos la actualización solo con los campos que han cambiado
            response = self.update_data(where_condition=where_condition, json_data=updated_data)
            return response
        else:
            print("No hubo cambios en los datos.")
            return None

    def get_data(self, where_condition=None, order_by=None, limit_clause=None, json_data=None, select_columns=None):
        response = self._make_request(
            procedure="select_json_entity",
            where_condition=where_condition,
            order_by=order_by,
            limit_clause=limit_clause,
            json_data=json_data,
            select_columns=select_columns
        )
        if response:
            return response.get('outputParams', {}).get('result', [])
        else:
            return []

    def delete_data(self, where_condition=None):
        return self._make_request(
            procedure="delete_json_entity",
            where_condition=where_condition
        )

    def insert_data(self, json_data=None):
        response = self._make_request(
            procedure="insert_json_entity", 
            json_data=json_data,  
        )

        if response is not None:
            pass
        else:
            pass
        
        return response
    
    def update_data(self, where_condition=None, json_data=None):
        """Actualiza los datos en la API usando la condición 'where' y los nuevos datos 'json_data'"""
        
        # Comprobamos si donde_condition o json_data están vacíos
        if not where_condition or not json_data:
            print("Faltan datos: where_condition o json_data son necesarios.")
            return None
        
        # Imprimimos los datos para asegurarnos de que son los correctos
        print(f"Condición WHERE: {where_condition}")
        print(f"Datos a actualizar: {json_data}")
        
        # Llamada a la API para actualizar los datos
        response = self._make_request(
            procedure="update_json_entity",  # Procedimiento de actualización
            where_condition=where_condition,  # Condición WHERE para especificar qué registros actualizar
            json_data=json_data  # Nuevos datos a actualizar
        )
        
        # Imprimimos la respuesta completa para depurar
        if response is not None:
            print(f"Respuesta de la API: {response}")
        else:
            print("No se recibió respuesta de la API.")
        
        return response










# Relación entre Idea y Usuario usando la API (sin utilizar modelos Django)
class IdeaUsuario:
    @staticmethod
    def get_idea_by_codigo(codigo_idea):
        try:
            # Crear cliente API
            client = APIClient('idea')
            
            # Generar la condición WHERE
            where_condition = f"codigo_idea = '{codigo_idea}'"
            
            # Realizar la solicitud para obtener los datos
            response = client.get_data(where_condition=where_condition)
            
            # Comprobar si la respuesta es válida
            if response:
                # Aquí no se encuentra la clave 'outputParams', por lo que directamente
                # trabajamos con la respuesta tal como viene.
                if isinstance(response, list) and len(response) > 0:
                    return response[0]
                else:
                    return None
            else:
                return None

        except requests.exceptions.RequestException as e:
            return None
        except Exception as e:
            return None

    @staticmethod
    def insert_idea_and_associate_user(form, user_email):
        """
        Inserta una nueva idea en la API y asocia al usuario con la idea.
        """
        # Obtener los objetos de foco de innovación y tipo de innovación desde las API
        try:
            focos = FocoInnovacionAPI.get_focos()  # Obtener los focos de innovación
            tipos = TipoInnovacionAPI.get_tipo_innovacion()  # Obtener los tipos de innovación

            # Buscar el foco de innovación y tipo de innovación usando el ID recibido del formulario
            foco_innovacion = next((foco for foco in focos if foco['id'] == form.cleaned_data['id_foco_innovacion']), None)
            tipo_innovacion = next((tipo for tipo in tipos if tipo['id'] == form.cleaned_data['id_tipo_innovacion']), None)

            # Verificar si los datos son válidos
            if not foco_innovacion or not tipo_innovacion:
                return False, "Error al obtener Foco de Innovación o Tipo de Innovación."

            # Crear los datos para la API
            json_data = {
                'titulo': form.cleaned_data['titulo'],
                'descripcion': form.cleaned_data['descripcion'],
                'palabras_claves': form.cleaned_data['palabras_claves'],
                'recursos_requeridos': form.cleaned_data['recursos_requeridos'],
                'fecha_creacion': form.cleaned_data['fecha_creacion'],
                'id_foco_innovacion': foco_innovacion['id'],  # ID del foco de innovación
                'id_tipo_innovacion': tipo_innovacion['id'],  # ID del tipo de innovación
                'creador_por': user_email
            }

            client = APIClient('idea')  # Inicialización del cliente API

            # Intentar insertar los datos en la API
            response = client.insert_data(json_data=json_data)

            if response and 'codigo_idea' in response:
                idea_codigo = response['codigo_idea']
                json_association = {
                    'email_usuario': user_email,
                    'codigo_idea': idea_codigo
                }

                # Asociar la idea con el usuario
                association_response = client.insert_data(json_data=json_association)

                return True, 'Idea creada y asociada exitosamente.'
            else:
                return False, 'Error al crear la idea. La respuesta de la API no es válida.'
        except requests.exceptions.RequestException as e:
            return False, f'Error de conexión con la API: {e}'
        except Exception as e:
            return False, f'Error inesperado: {e}'

# Función para guardar el archivo multimedia en el servidor
def save_archivo(archivo):
    # Usar FileSystemStorage para guardar el archivo
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    nombre_archivo = fs.save(archivo.name, archivo)  # Guarda el archivo y obtiene el nombre
    archivo_ruta = fs.url(nombre_archivo)  # Obtener la URL del archivo guardado
    return archivo_ruta

# Función para crear la idea y asociarla con el usuario
def crear_idea_y_asociar_usuario(request, form):
    if not form.is_valid():
        messages.error(request, 'Formulario no válido. Por favor, verifica los datos.')
        return redirect('ideas:create')

    user_email = request.user.email
    archivo = request.FILES.get('archivo_multimedia')  # Obtener el archivo multimedia del formulario

    success, message = IdeaUsuario.insert_idea_and_associate_user(form, user_email, archivo)

    if success:
        messages.success(request, message)
        return redirect('ideas:list')  # Redirige a la lista de ideas
    else:
        messages.error(request, message)
        return redirect('ideas:create')  # Redirige a la página de creación
