from django.db import models

# Create your models here.
# Create content/models.py

from django.db import models
from django.conf import settings

class BlogPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    prompt = models.TextField()
    content = models.TextField()
    tokens_used = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
