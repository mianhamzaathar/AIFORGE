from django.db import models


from django.db import models
from django.conf import settings

class Plan(models.Model):
    PLAN_TYPES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=50, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tokens = models.IntegerField()
    features = models.TextField()
    stripe_price_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.tokens} tokens"

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan}"
