from rest_framework import serializers
from .models import Cart, Product, Customisation


class ProductSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "p_desc", "p_size", "p_finish", "p_flex", "p_textures"]


class CustomisationSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customisation
        fields = ["id", "p_size", "p_finish", "p_flex", "p_textures"]


class CartSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)
    design = CustomisationSimpleSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id", "user_id", "product", "design",
            "quantity", "unit_price", "created_at", "updated_at"
        ]