import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse

SECRET_KEY = settings.SECRET_KEY

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('Authorization')

        if token:
            try:
                # Eliminar "Bearer" del token y decodificar
                token = token.split(' ')[1]
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

                # Obtener el usuario con el ID del payload
                user = get_user_model().objects.get(id=payload['user_id'])
                request.user = user

            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expirado'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Token inválido'}, status=401)

        else:
            request.user = None  # No autenticado

        response = self.get_response(request)
        return response
