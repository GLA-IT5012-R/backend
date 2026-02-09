from rest_framework import serializers
from .models import Product, ProductAsset, ProductAssetLink

class ProductAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAsset
        fields = [
            "id", "type", "type_id", "type_name", "texture_urls", "created_at", "updated_at"
        ]

class ProductSerializer(serializers.ModelSerializer):
    # 单品只取第一个 asset 的技术信息
    asset = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "type", "price", "status",
            "p_desc", "p_size", "p_finish", "p_flex", "p_textures",
            "asset"
        ]

    def get_asset(self, obj):
        # 通过 link 表取对应 asset
        link = obj.asset_links.first()  # 只取第一条
        if link and link.asset:
            return ProductAssetSerializer(link.asset).data
        return None
