
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls', namespace='authentication')),
    path('', include('ideas.urls', namespace='ideas')),
    path('', include('oportunidades.urls', namespace='oportunidades')),
    path('', include('perfil.urls', namespace='perfil')),  
]