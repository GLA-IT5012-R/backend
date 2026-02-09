# api/models.py
from django.db import models


# UserProfile 模型，用于存储从 Clerk 同步过来的用户信息
class UserProfile(models.Model):
    clerk_id = models.CharField(max_length=255, unique=True)  # Clerk 给的 user ID
    email = models.EmailField()
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)  # 可选字段
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.email

