

from django.urls import include, path
from .views import (
    login,
    home,
    app
)

app_name = 'authentication'

urlpatterns = [
    path('', home.home, name='home'),
    path('app/', app.app, name='app'),
    path('login/', login.user_login, name='user_login'), 
  
]
