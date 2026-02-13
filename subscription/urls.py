# Create subscription/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('checkout/<int:plan_id>/', views.create_checkout_session, name='checkout'),
    path('buy-tokens/', views.buy_tokens, name='buy_tokens'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('tokens-added/', views.tokens_added, name='tokens_added'),
]
