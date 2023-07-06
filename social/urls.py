from django.urls import path
from .views import room
from . import views
urlpatterns = [
    path('<str:uuid>/', room, name='room'),
]