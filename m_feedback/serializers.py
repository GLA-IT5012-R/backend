# api/serializers.py
from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "rating",
            "comment",
            "created_at",
        ]

    def get_user(self, obj):
        return {
            "username": obj.user.name  # 你没有 username 字段，用 name 替代
        }

    def get_product(self, obj):
        return {
            "id": obj.product.id,
            "name": obj.product.name
        }

