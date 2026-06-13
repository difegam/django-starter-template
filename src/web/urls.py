from django.urls import path

from .views import health, home

app_name = 'web'

urlpatterns = [
    path('', home, name='home'),
    path('health/', health, name='health'),
]
