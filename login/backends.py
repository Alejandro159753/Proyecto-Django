# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.hashers import check_password  # Importa la función check_password
# from .models import Usuario
# from django.conf import settings
# import requests

# class CustomAuthBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         print("Iniciando autenticación en CustomAuthBackend")
#         print(f"Parámetros recibidos - Username: {username}, Password: {password}")
        
#         api_url = f"{settings.API_URL.rstrip('/')}/usuario"
        
#         request_body = {
#             "procedure": "select_json_entity",
#             "parameters": {
#                 "table_name": "usuario",
#                 "where_condition": "email = %(email)s",
#                 "json_data": {
#                     "email": username
#                 },
#                 "select_columns": "email, contrasena"
#             }
#         }

#         headers = {"Content-Type": "application/json"}

#         try:
#             response = requests.get(api_url, params=request_body, headers=headers)
#             print(f"API URL: {api_url}")
#             print(f"Status Code: {response.status_code}")
#             print(f"Response Content: {response.content}")

#             if response.status_code == 200:
#                 data = response.json()
#                 print(f"Datos recibidos de la API: {data}")
                
#                 if data:
#                     user_data = data[0]  # La respuesta es una lista, obtenemos el primer elemento
#                     print(f"Usuario obtenido de la API: {user_data}")
                    
#                     if 'contrasena' in user_data:
#                         print(f"Contraseña en base de datos: {user_data['contrasena']}")
#                         print(f"Contraseña proporcionada: {password}")
                        
#                         # Usamos check_password para comparar las contraseñas de forma segura
#                         if check_password(password, user_data['contrasena']):
#                             print("Autenticación exitosa en el backend.")
#                             # Aseguramos que el email se crea si no existe en el modelo Usuario
#                             usuario, created = Usuario.objects.get_or_create(email=username)
#                             return usuario
#                         else:
#                             print("Contraseña incorrecta.")
#                     else:
#                         print("No se encontró el campo 'contrasena' en los datos de usuario.")
#                 else:
#                     print("No se encontraron datos de usuario en la respuesta.")
#             else:
#                 print(f"Error en la solicitud a la API. Código de estado: {response.status_code}")
#         except requests.exceptions.RequestException as e:
#             print(f"Error en la llamada a la API: {e}")

#         return None

#     def get_user(self, user_id):
#         try:
#             # Se obtiene el usuario por su ID (que es el email en este caso)
#             return Usuario.objects.get(pk=user_id)
#         except Usuario.DoesNotExist:
#             return None


import requests
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings


class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        api_url = f"{settings.API_URL}usuario"
        


        request_body = {
            "procedure": "select_json_entity",
            "parameters": {
                "table_name": "usuario",
                "where_condition": "email = %(email)s",
                "json_data": {
                    "email": username
                },
                "select_columns": "email, password"
            }
        }
        response = requests.get(api_url, json=request_body)
        api_url = f"{settings.API_URL}usuario"
        print(f"API URL: {api_url}")  # Agrega esta línea para verificar la URL
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")
        if response.status_code == 200:
            data = response.json()
            if data and data[0]['password'] == password:
                return User.objects.get_or_create(username=username)[0]
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
