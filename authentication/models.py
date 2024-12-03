import os
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
import requests

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
