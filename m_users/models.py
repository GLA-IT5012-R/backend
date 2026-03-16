# api/models.py
from django.db import models

# UserProfile model ,  form Clerk user info synced to our UserProfile
class UserProfile(models.Model):
    clerk_id = models.CharField(max_length=255, unique=True)  # Clerk -- user ID
    email = models.EmailField()
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "m_user_profiles"
    def __str__(self):
        return self.name or self.email

