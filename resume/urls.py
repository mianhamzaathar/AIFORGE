from django.urls import path
from . import views

urlpatterns = [
    path('', views.resume_optimizer, name='resume_optimizer'),
]
