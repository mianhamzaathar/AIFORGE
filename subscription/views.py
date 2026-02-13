from django.shortcuts import render

# Create your views here.
# Create subscription/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Plan
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def pricing(request):
    plans = Plan.objects.all()
    return render(request, 'subscription/pricing.html', {'plans': plans})

@login_required
def create_checkout_session(request, plan_id):
    plan = Plan.objects.get(id=plan_id)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(plan.price * 100),
                        'product_data': {
                            'name': f"{plan.get_name_display()} Plan",
                            'description': f"{plan.tokens} AIForge Tokens",
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/subscription/success/'),
            cancel_url=request.build_absolute_uri('/subscription/cancel/'),
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id,
                'tokens': plan.tokens
            }
        )
        return redirect(checkout_session.url)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('pricing')

@login_required
def payment_success(request):
    messages.success(request, '✅ Payment successful! Tokens added to your account.')
    return redirect('dashboard')

@login_required
def payment_cancel(request):
    messages.warning(request, 'Payment was cancelled.')
    return redirect('pricing')

@login_required
def buy_tokens(request):
    if request.method == 'POST':
        tokens = int(request.POST.get('tokens', 100))
        amount = tokens / 10
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(amount * 100),
                            'product_data': {
                                'name': f"{tokens} AIForge Tokens",
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri('/subscription/tokens-added/'),
                cancel_url=request.build_absolute_uri('/subscription/cancel/'),
                metadata={
                    'user_id': request.user.id,
                    'tokens': tokens
                }
            )
            return redirect(checkout_session.url)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'subscription/buy_tokens.html')

@login_required
def tokens_added(request):
    messages.success(request, '✨ Tokens added successfully!')
    return redirect('dashboard')
