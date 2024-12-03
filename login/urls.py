# login/urls.py

from django.urls import path
from .views.login import login_view  # Importa la función de vista directamente
from .views.logout import logout_view  # Importa la vista logout
from .views.register import registro_usuario  # Importa la vista de registro

app_name = 'login'

urlpatterns = [
    path('login/', login_view, name='login'),  # Asegúrate de que login_view esté bien importada
    path('logout/', logout_view, name='logout'),
    path('registro/', registro_usuario, name='register'),
]
