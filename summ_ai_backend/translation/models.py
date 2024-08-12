from django.contrib.auth.models import User
from django.db import models

class Translation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_text = models.TextField()
    translated_text = models.TextField()
    content_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        # String representation of the Translation model instance
        return f'Translation {self.id} by {self.user.username}'