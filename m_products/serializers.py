from rest_framework import serializers
from .models import Product, ProductAsset, ProductAssetLink

class ProductAssetSerializer(serializers.ModelSerializer):
    asset_id = serializers.IntegerField(source="id")
    
    class Meta:
        model = ProductAsset
        fields = [
            "asset_id", "type", "asset_code", "texture_urls"
        ]

class ProductSerializer(serializers.ModelSerializer):
    # single asset for normal product, multiple assets for bundle
    asset = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "type", "price", "status",
            "p_desc", "p_size", "p_finish", "p_flex", "p_textures","is_double_sided",
            "asset"
        ]

    def get_asset(self, obj):
        # look for linked assets, if it's a bundle, it can have multiple assets, we return the first one for simplicity
        link = obj.asset_links.first()  # assuming one asset per product for now, can be extended to multiple if needed
        if link and link.asset:
            return ProductAssetSerializer(link.asset).data
        return None
