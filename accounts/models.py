from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    token_balance = models.IntegerField(default=1000)
    subscription_plan = models.CharField(max_length=50, default='free')
    subscription_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    def deduct_tokens(self, amount, service_type):
        """Deduct tokens from user balance"""
        if self.token_balance >= amount:
            self.token_balance -= amount
            self.save()
            TokenTransaction.objects.create(
                user=self,
                amount=-amount,
                service_type=service_type,
                balance_after=self.token_balance
            )
            return True
        return False
    
    def add_tokens(self, amount):
        """Add tokens to user balance"""
        self.token_balance += amount
        self.save()
        TokenTransaction.objects.create(
            user=self,
            amount=amount,
            service_type='purchase',
            balance_after=self.token_balance
        )

class TokenTransaction(models.Model):
    SERVICE_TYPES = [
        ('blog', '📝 Blog Writing'),
        ('image', '🎨 Image Generation'),
        ('resume', '📄 Resume Optimizer'),
        ('codehelper', '💻 Code Explain'),  # ✅ FIXED: Removed space after 'codehelper'
        ('purchase', '💰 Token Purchase'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    amount = models.IntegerField()
    service_type = models.CharField(
        max_length=20, 
        choices=SERVICE_TYPES,
        db_index=True  # ✅ Added for better performance
    )
    balance_after = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # ✅ Added index
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Token Transaction'  # ✅ Added for admin
        verbose_name_plural = 'Token Transactions'  # ✅ Added for admin
    
    def __str__(self):
        return f"{self.user.username} - {self.get_service_type_display()} - {self.amount}"