from django.db import models

# Pruduct 模型，用于存储商品信息
class ProductAsset(models.Model):
    """
    单品资源
    """

    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=50)  # snowboard / goggles / clothing
    type_id = models.CharField(max_length=50, unique=True)  # SB-001, GOG-001

    # ---------- 保留技术相关 ----------
    texture_urls = models.JSONField(
        default=dict, help_text='例如 {"SB-001": ["front.png", "back.png"]}'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_product_assets"

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

    # ---------- 新增字段 ----------
    p_desc = models.TextField(blank=True, help_text="产品描述")
    p_size = models.CharField(
        max_length=100, default="0", help_text="例如 140,160,180；无尺寸用 0"
    )
    p_finish = models.CharField(
        max_length=50, blank=True, help_text="板面工艺，例如 matte / glossy"
    )
    p_flex = models.CharField(
        max_length=50, blank=True, help_text="软硬度，例如 soft / regular / stiff"
    )
    p_textures = models.JSONField(default=dict, blank=True, help_text="产品纹理JSON")

    is_double_sided = models.BooleanField(
        default=False,
        help_text="是否双面纹理：False 表示单面，True 表示正反使用同一张图"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_products"

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
        # limit_choices_to={"type": 2},  # 只允许套装
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
        return f"{self.product.name} -> {self.asset.name} x {self.quantity}"

class Customisation(models.Model):
    """
    用户定制记录表
    """
    id = models.BigAutoField(primary_key=True)

    # ---------- 关联用户和产品 ----------
    user_id = models.BigIntegerField(help_text="用户ID")  # 可用 FK -> User，如果有用户模型的话
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="customisations",
        help_text="用户定制的产品",
    )

    # ---------- 核心定制字段（拆开存，方便查询/修改/统计） ----------
    p_size = models.CharField(
        max_length=50, blank=True, help_text="用户选择尺寸，例如 160"
    )
    p_finish = models.CharField(
        max_length=50, blank=True, help_text="用户选择板面工艺，例如 glossy"
    )
    p_flex = models.CharField(
        max_length=50, blank=True, help_text="用户选择软硬度，例如 soft"
    )
    # 如果纹理多选或者组合复杂，使用 JSON 存储
    p_textures = models.JSONField(
        default=list, blank=True, help_text="用户选择纹理，可能多个，存 JSON"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_customisations"

    def __str__(self):
        return f"Customisation {self.id} - User {self.user_id} - Product {self.product.name}"

