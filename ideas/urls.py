from django.urls import path
# from .views.ideas import base
from .views.ideas import list_ideas, create_idea, update_idea, delete_idea, detail_idea,confirmar_idea

app_name = 'ideas'

urlpatterns = [

    path('list/', list_ideas, name='list'),
    path('create/', create_idea, name='create'),
    path('update/<pk>/', update_idea, name='update'),
    path('delete/<pk>/', delete_idea, name='delete'),
    path('detail/<int:codigo_idea>/', detail_idea, name='detail'),
    path('idea/confirmar/<int:codigo_idea>/', confirmar_idea, name='confirmar_idea'),
]
