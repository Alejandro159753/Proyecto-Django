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
            print("Faltan datos para la actualización.")
            return None

        # Paso 1: Obtener los datos actuales de la API
        current_data = self.get_data(where_condition=where_condition)
        if not current_data:
            print("No se encontraron datos actuales para la oportunidad.")
            return None

        current_data = current_data[0]  # Si solo hay un resultado, lo tomamos

        # Paso 2: Comparar los datos actuales con los nuevos datos
        updated_data = {}
        for key, value in json_data.items():
            if current_data.get(key) != value:
                updated_data[key] = value

        # Paso 3: Realizar la actualización solo si hay datos que han cambiado
        if updated_data:
            print(f"Datos actualizados: {updated_data}")
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
class SolucionUsuario:
    @staticmethod
    def get_solucion_by_codigo(codigo_solucion):
        """
        Obtiene una solución por su código desde la API.
        """
        try:
            client = APIClient('solucion')
            where_condition = f"codigo_solucion = '{codigo_solucion}'"
            response = client.get_data(where_condition=where_condition)

            if response:
                # Asegurarnos de que la respuesta es una lista no vacía
                if isinstance(response, list) and len(response) > 0:
                    return response[0]
                else:
                    print(f"No se encontró la solución con código: {codigo_solucion}")
                    return None
            else:
                print("Error: la respuesta de la API es vacía")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener la solución: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None

    @staticmethod
    def insert_solucion_and_associate_user(form, user_email):
        """
        Inserta una nueva solución en la API y asocia al usuario con la solución.
        """
        try:
            # Obtener los objetos de foco de innovación y tipo de innovación desde las API
            focos = FocoInnovacionAPI.get_focos()  # Obtener los focos de innovación
            tipos = TipoInnovacionAPI.get_tipo_innovacion()  # Obtener los tipos de innovación

            # Buscar el foco de innovación y tipo de innovación usando el ID recibido del formulario
            foco_innovacion = next((foco for foco in focos if foco['id'] == form.cleaned_data['id_foco_innovacion']), None)
            tipo_innovacion = next((tipo for tipo in tipos if tipo['id'] == form.cleaned_data['id_tipo_innovacion']), None)

            # Verificar si los datos son válidos
            if not foco_innovacion or not tipo_innovacion:
                return False, "Error al obtener Foco de Innovación o Tipo de Innovación."

            # Crear los datos para la API para la 'solución'
            json_data = {
                'titulo': form.cleaned_data['titulo'],
                'descripcion': form.cleaned_data['descripcion'],
                'palabras_claves': form.cleaned_data['palabras_claves'],
                'recursos_requeridos': form.cleaned_data['recursos_requeridos'],
                'fecha_creacion': form.cleaned_data['fecha_creacion'],
                'id_foco_innovacion': foco_innovacion['id'],  # ID del foco de innovación
                'id_tipo_innovacion': tipo_innovacion['id'],  # ID del tipo de innovación
                'creador_por': user_email,
                'quien_desarrollo': form.cleaned_data['quien_desarrollo'],  # Campo adicional
                'area_unidad_desarrollo': form.cleaned_data['area_unidad_desarrollo']  # Campo adicional
            }

            client = APIClient('solucion')  # Inicialización del cliente API para 'solución'

            # Intentar insertar los datos en la API para la solución
            response = client.insert_data(json_data=json_data)

            if response and 'codigo_solucion' in response:
                solucion_codigo = response['codigo_solucion']
                json_association = {
                    'email_usuario': user_email,
                    'codigo_solucion': solucion_codigo
                }

                # Asociar la solución con el usuario
                association_response = client.insert_data(json_data=json_association)

                return True, 'Solución creada y asociada exitosamente.'
            else:
                return False, 'Error al crear la solución. La respuesta de la API no es válida.'
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