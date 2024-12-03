from django.urls import path
# from .views.ideas import base
from .views.oportunidades import list_oportunidades, create_oportunidad, update_oportunidad, delete_oportunidad,detail_oportunidad,confirmar_oportunidad

app_name = 'oportunidades'

urlpatterns = [

    path('list_oportunidad/', list_oportunidades, name='list_oportunidad'),
    path('create_oportunidad/', create_oportunidad, name='create'),
    path('update_oportunidades/<int:codigo_oportunidad>/', update_oportunidad, name='update_oportunidades'),
    path('delete_oportunidades/<int:codigo_oportunidad>/', delete_oportunidad, name='delete_oportunidades'),
    path('detail_oportunidades/<int:codigo_oportunidad>/', detail_oportunidad, name='detail_oportunidades'),
    path('oportunidad/confirmar/<int:codigo_oportunidad>/', confirmar_oportunidad, name='confirmar_oportunidad'),
    ]