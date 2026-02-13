from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TokenTransaction

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    list_display = ['username', 'email', 'token_balance', 'subscription_plan', 'is_active', 'created_at']
    list_filter = ['subscription_plan', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Token & Subscription', {
            'fields': ('token_balance', 'subscription_plan', 'subscription_end')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Personal Info', {
            'fields': ('email', 'token_balance', 'subscription_plan')
        }),
    )

@admin.register(TokenTransaction)
class TokenTransactionAdmin(admin.ModelAdmin):
    """Token Transaction Admin"""
    list_display = ['user', 'get_service_type_display', 'amount', 'balance_after', 'created_at']
    list_filter = ['service_type', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False  # Transactions are created automatically