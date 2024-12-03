

from django.urls import include, path
from .views import (

    home,
    app,
    dashboard,
    
)

app_name = 'authentication'

urlpatterns = [
    path('', home.home, name='home'),
    path('app/', app.app, name='app'),
    path('dashboard/', dashboard.dashboard_view, name='dashboard'),
    path('notificaciones/marcar_leida/', app.marcar_leida, name='marcar_leida'),
    path('notificaciones/eliminar/', app.eliminar_notificacion, name='eliminar_notificacion'),
    path('proyectos/', app.listar_proyectos, name='listar_proyectos'),
 
  
]
