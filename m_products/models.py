from django.db import models
from m_users.models import UserProfile


# Product model, used to store product info
class ProductAsset(models.Model):
    """
    单品资源
    """

    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=50)  # snowboard / goggles / clothing
    asset_code = models.CharField(max_length=50, unique=True)  # SB-001, GOG-001

    # ---------- texture urls ----------
    texture_urls = models.JSONField(
        default=dict, help_text='例如 {"SB-001": ["front.png", "back.png"]}'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_product_assets"

    def __str__(self):
        return f"{self.type} - {self.asset_code}"


class Product(models.Model):
    """
    type: 1 single, 2 bundle
    """

    class ProductType(models.IntegerChoices):
        SINGLE = 1, "single"
        BUNDLE = 2, "bundle"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    type = models.IntegerField(choices=ProductType.choices, default=ProductType.SINGLE)
    status = models.BooleanField(default=True, help_text="is product active?")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="product price in pound, e.g. 199.99",
    )

    p_desc = models.TextField(blank=True, help_text="product description")
    p_size = models.CharField(
        max_length=100, default="0", help_text="e.g. 140,160,180; no size use 0"
    )
    p_finish = models.CharField(
        max_length=50, blank=True, help_text="board finish, e.g. matte / glossy"
    )
    p_flex = models.CharField(
        max_length=50, blank=True, help_text="flexibility, e.g. soft / regular / stiff"
    )
    p_textures = models.JSONField(default=list, blank=True, help_text="product textures JSON")

    is_double_sided = models.BooleanField(
        default=False,
        help_text="is double sided texture: False means single sided, True means both sides use the same image",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_products"

    def __str__(self):
        return self.name


class ProductAssetLink(models.Model):
    """
    product and asset link table, used to link products and assets, especially for bundles
    """

    id = models.BigAutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="asset_links",
        # limit_choices_to={"type": 2},  # only allow bundles
    )

    asset = models.ForeignKey(
        ProductAsset,
        on_delete=models.CASCADE,
        related_name="product_links",
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "m_product_asset_links"
        unique_together = ("product", "asset")

    def __str__(self):
        return f"{self.product.name} -> {self.asset.asset_code} x {self.quantity}"


class Customisation(models.Model):
    """
    user customisation record, used to store user customisation choices for a product
    """

    id = models.BigAutoField(primary_key=True)

    # ---------- user and product ----------
   
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="customisations", null=True, blank=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="customisations",
        help_text="user customised product",
    )

    # ---------- 核心定制字段（拆开存，方便查询/修改/统计） ----------
    p_size = models.CharField(
        max_length=50, blank=True, help_text="user selected size, e.g. 160"
    )
    p_finish = models.CharField(
        max_length=50, blank=True, help_text="user selected board finish, e.g. glossy"
    )
    p_flex = models.CharField(
        max_length=50, blank=True, help_text="user selected flexibility, e.g. soft"
    )
    # if multiple or complex texture choices, use JSON to store
    p_textures = models.JSONField(
        default=list, blank=True, help_text="user selected textures, possibly multiple, stored as JSON"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_customisations"

    def __str__(self):
        return f"Customisation {self.id} - User {self.user_id} - Product {self.product.name}"
