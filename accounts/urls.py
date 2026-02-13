from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Dashboard & Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Additional user routes (optional - uncomment if you have these views)
    # path('settings/', views.settings, name='settings'),
    # path('change-password/', views.change_password, name='change_password'),
    # path('delete-account/', views.delete_account, name='delete_account'),
]