# Create content/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('write/', views.blog_writer, name='blog_writer'),
    path('my-blogs/', views.my_blogs, name='my_blogs'),
    path('view/<int:blog_id>/', views.view_blog, name='view_blog'),
    path('improve/<int:blog_id>/', views.improve_blog, name='improve_blog'),
]
