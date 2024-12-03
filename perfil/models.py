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
        response = self._make_request(
            procedure="select_json_entity",
            where_condition=where_condition,
            order_by=order_by,
            limit_clause=limit_clause,
            json_data=json_data,
            select_columns=select_columns
        )
        result = response.get('outputParams', {}).get('result', []) if response else []
        return result

    def delete_data(self, where_condition=None):
        response = self._make_request(
            procedure="delete_json_entity",
            where_condition=where_condition
        )
        return response

    def insert_data(self, json_data=None):
        response = self._make_request(
            procedure="insert_json_entity", 
            json_data=json_data,  
        )

        return response
    
    def update_data(self, where_condition=None, json_data=None):
        """Actualiza los datos en la API usando la condición 'where' y los nuevos datos 'json_data'"""
        if not where_condition or not json_data:
            return None
        
        response = self._make_request(
            procedure="update_json_entity",  # Procedimiento de actualización
            where_condition=where_condition,  # Condición WHERE para especificar qué registros actualizar
            json_data=json_data  # Nuevos datos a actualizar
        )
        
        return response
    

class FocoInnovacionAPI:
    @staticmethod
    def get_focos():
        api_url = "http://190.217.58.246:5186/api/sgv/foco_innovacion"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
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
            return []
