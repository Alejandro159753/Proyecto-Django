from django.urls import path
# from .views.ideas import base
from .views.solucion import list_soluciones, create_solucion, update_solucion, delete_solucion,detail_solucion, confirmar_solucion

app_name = 'soluciones'

urlpatterns = [

    path('list_solucion/', list_soluciones, name='list_soluciones'),
    path('create_solucion/', create_solucion, name='create'),
    path('update_soluciones/<int:codigo_solucion>/', update_solucion, name='update_soluciones'),
    path('delete_soluciones/<int:codigo_solucion>/', delete_solucion, name='delete_soluciones'),
    path('detail_soluciones/<int:codigo_solucion>/', detail_solucion, name='detail_soluciones'),
    path('solucion/confirmar/<int:codigo_solucion>/', confirmar_solucion, name='confirmar_solucion'),
    ]