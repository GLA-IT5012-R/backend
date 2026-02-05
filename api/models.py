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


# Pruduct 模型，用于存储商品信息
class ProductAsset(models.Model):
    """
    单品资源（雪板 / 眼镜 / 衣服等）
    """

    id = models.BigAutoField(primary_key=True)

    type = models.CharField(max_length=50)  # snowboard / goggles / clothing
    type_id = models.CharField(max_length=50, unique=True)  # SB-001
    type_name = models.CharField(max_length=100)  # 雪板_0011

    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)

    

    size = models.CharField(
        max_length=100, default="0", help_text="例如 140,160,180；无尺寸用 0"
    )

    topsheet_finish = models.CharField(
        max_length=50, blank=True, help_text="板面工艺，例如 matte / gloss"
    )

    flex = models.CharField(
        max_length=50, blank=True, help_text="软硬度，例如 soft / regular / stiff"
    )

    # ===================

    texture_urls = models.JSONField(
        default=dict, help_text='例如 {"SB-001": ["front.png", "back.png"]}'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_assets"

    def __str__(self):
        return f"{self.type_name} - {self.name}"


class Product(models.Model):
    """
    对外售卖的产品（单品 / 套装）
    """

    class ProductType(models.IntegerChoices):
        SINGLE = 1, "单品"
        BUNDLE = 2, "套装"

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=255)

    type = models.IntegerField(choices=ProductType.choices, default=ProductType.SINGLE)

    status = models.BooleanField(default=True, help_text="是否上架")
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="product price in pound, e.g. 199.99",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name


class ProductAssetLink(models.Model):
    """
    套装与单品资源的关联表
    """

    id = models.BigAutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="asset_links",
        limit_choices_to={"type": 2},  # 只允许套装
    )

    asset = models.ForeignKey(
        ProductAsset,
        on_delete=models.CASCADE,
        related_name="product_links",
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "product_asset_links"
        unique_together = ("product", "asset")

    def __str__(self):
        return f"{self.product.name} -> {self.asset.name} x {self.quantity}"
