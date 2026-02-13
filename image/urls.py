from django.urls import path
from . import views

urlpatterns = [
    path('', views.image_generator, name='image_generator'),
]
