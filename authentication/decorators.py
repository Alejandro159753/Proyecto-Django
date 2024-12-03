import jwt
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from functools import wraps
from django.shortcuts import redirect

def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Intentar obtener el token de las cabeceras de la solicitud
        token = request.META.get('HTTP_AUTHORIZATION')
        
        if not token:
            return JsonResponse({'error': 'Token no proporcionado'}, status=401)
        
        try:
            # Eliminar 'Bearer ' si está presente
            token = token.split(' ')[1]
            # Verificar el token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user = payload['user']  # Suponiendo que el token contiene el id o email del usuario
        except (IndexError, InvalidToken, TokenError):
            return JsonResponse({'error': 'Token inválido o expirado'}, status=401)

        return view_func(request, *args, **kwargs)
    
    return _wrapped_view