
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', include('authentication.urls', namespace='authentication')),
    path('login/', include('login.urls', namespace='login')), 
    path('ideas/', include('ideas.urls', namespace='ideas')),
    path('oportunidades/', include('oportunidades.urls', namespace='oportunidades')),
    path('soluciones/', include('soluciones.urls', namespace='soluciones')),
    path('perfil/', include('perfil.urls',namespace='perfil')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)