from django.urls import path
from . import views

urlpatterns = [
    path('', views.nal, name='nal'),
]