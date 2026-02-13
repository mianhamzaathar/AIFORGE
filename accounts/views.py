from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.db.models import Sum, Count
from .models import User, TokenTransaction

class CustomUserCreationForm(forms.ModelForm):
    """Custom User Creation Form for accounts.User"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('❌ Passwords do not match!')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.token_balance = 1000  # Give free tokens
        if commit:
            user.save()
        return user

def home(request):
    """Home page"""
    return render(request, 'accounts/home.html')

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '🎉 Welcome to AIForge! You got 1000 free tokens!')
            return redirect('dashboard')
        else:
            # Form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'✅ Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, '❌ Invalid username or password!')
    return render(request, 'accounts/login.html')

def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, '✅ Logged out successfully!')
    return redirect('home')

@login_required
def dashboard(request):
    """User dashboard with statistics"""
    # Get user stats
    total_tokens_used = TokenTransaction.objects.filter(
        user=request.user, 
        amount__lt=0
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent transactions
    recent_transactions = TokenTransaction.objects.filter(
        user=request.user
    )[:10]
    
    # Service usage stats
    service_stats = TokenTransaction.objects.filter(
        user=request.user,
        amount__lt=0
    ).values('service_type').annotate(
        count=Count('id'),
        tokens=Sum('amount')
    )
    
    context = {
        'user': request.user,
        'total_tokens_used': abs(total_tokens_used),
        'recent_transactions': recent_transactions,
        'service_stats': service_stats,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    """User profile"""
    if request.method == 'POST':
        # Update profile
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save()
            messages.success(request, '✅ Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'accounts/profile.html', {'user': request.user})