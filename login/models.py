import requests
from django.conf import settings

class APIClient:
    BASE_URL = "http://190.217.58.246:5186/api/SGV/procedures/execute"  # URL actualizada

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
            
            return None
        except Exception as e:
            
            return None

    def get_data(self, where_condition=None, order_by=None, limit_clause=None, json_data=None, select_columns=None):
        return self._make_request(
            procedure="select_json_entity",
            where_condition=where_condition,
            order_by=order_by,
            limit_clause=limit_clause,
            json_data=json_data,
            select_columns=select_columns
        ).get('outputParams', {}).get('result', [])

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
        return response
     
    
    def update_data(self, where_condition=None, json_data=None):
        return self._make_request(
            procedure="update_json_entity",
            where_condition=where_condition,
            json_data=json_data
        )

import requests
from django.conf import settings
from django.contrib.auth.hashers import check_password

class Usuario:
    @staticmethod
    def authenticate(email, password):
        api_url = f"{settings.API_URL}"
        payload = {
            "procedure": "select_json_entity",
            "parameters": {
                "table_name": "usuario",
                "select_columns": "email, password",
                "where_condition": f"email = '{email}'"
            }
        }

        # Realizar la solicitud a la API
        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            users = response.json()
            user = users['outputParams']['result'][0] if users['outputParams']['result'] else None

            if user:
                # Comparar la contraseña en texto plano con la encriptada utilizando check_password
                if check_password(password, user['password']):
                    return user  # Devuelve el usuario si la contraseña es correcta
        return None

    @staticmethod
    def get_profile_data(email):
        api_url = f"{settings.API_URL}"
        
        # Obtener los datos básicos del perfil
        profile_payload = {
            "procedure": "select_json_entity",
            "parameters": {
                "table_name": "perfil",
                "select_columns": "nombre, rol, fecha_nacimiento, direccion, descripcion",
                "where_condition": f"usuario_email = '{email}'"
            }
        }
        response = requests.post(api_url, json=profile_payload)
        profile_data = {}

        if response.status_code == 200:
            profiles = response.json()
            profile = profiles['outputParams']['result'][0] if profiles['outputParams']['result'] else None
            
            if profile:
                profile_data = profile  # Almacena los datos del perfil

        # Obtener info adicional de la tabla 'informacion_adicional'
        info_payload = {
            "procedure": "select_json_entity",
            "parameters": {
                "table_name": "informacion_adicional",
                "select_columns": "info",
                "where_condition": f"usuario_email = '{email}'"
            }
        }
        info_response = requests.post(api_url, json=info_payload)

        if info_response.status_code == 200:
            info_result = info_response.json()
            info_adicional = info_result['outputParams']['result'][0].get('info', '') if info_result['outputParams']['result'] else ''
            profile_data['info_adicional'] = info_adicional

        # Obtener área de expertise de la tabla 'areas_expertise'
        expertise_payload = {
            "procedure": "select_json_entity",
            "parameters": {
                "table_name": "areas_expertise",
                "select_columns": "area",
                "where_condition": f"usuario_email = '{email}'"
            }
        }
        expertise_response = requests.post(api_url, json=expertise_payload)

        if expertise_response.status_code == 200:
            expertise_result = expertise_response.json()
            area_expertise = expertise_result['outputParams']['result'][0].get('area', '') if expertise_result['outputParams']['result'] else ''
            profile_data['area_expertise'] = area_expertise

        return profile_data if profile_data else None