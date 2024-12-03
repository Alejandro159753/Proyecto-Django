from django.urls import path
# from .views.ideas import base
from .views.oportunidades import list_oportunidad, create_oportunidad, update_oportunidad, delete_oportunidad

app_name = 'oportunidades'

urlpatterns = [

    path('list_oportunidad/', list_oportunidad, name='list'),
    path('create_oportunidad/', create_oportunidad, name='create'),
    path('update/<int:pk>/', update_oportunidad, name='update'),
    path('delete/<int:pk>/', delete_oportunidad, name='delete'),

    ]