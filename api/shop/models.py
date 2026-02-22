from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Product(models.Model):
    """产品模型"""
    class ProductType(models.IntegerChoices):
        SINGLE = 1, '单品'
        SUITE = 2, '套装'

    name = models.CharField('产品名称', max_length=200)
    type = models.IntegerField('类型', choices=ProductType.choices, default=ProductType.SINGLE)
    status = models.BooleanField('上架状态', default=True)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    p_desc = models.TextField('产品描述', blank=True)
    p_size = models.CharField('尺寸', max_length=200, blank=True)
    p_finish = models.CharField('材质/表面工艺', max_length=100, blank=True)
    p_flex = models.CharField('弹性/硬度', max_length=100, blank=True)
    p_text = models.CharField('定制logo文字', max_length=500, blank=True)
    p_textures = models.JSONField('纹理', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = '产品'
        verbose_name_plural = '产品'

    def __str__(self):
        return self.name


class ProductAsset(models.Model):
    """产品资源模型（图片、3D模型等）"""
    name = models.CharField('资源名称', max_length=200)
    type = models.CharField('资源类型', max_length=50)  # 例如: 'snowboard', 'binding'
    texture_urls = models.JSONField('纹理URL', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'product_assets'
        verbose_name = '产品资源'
        verbose_name_plural = '产品资源'

    def __str__(self):
        return self.name


class ProductAssetLink(models.Model):
    """产品和资源的关联表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='asset_links')
    asset = models.ForeignKey(ProductAsset, on_delete=models.CASCADE, related_name='product_links')
    quantity = models.IntegerField('数量', default=1)

    class Meta:
        db_table = 'product_asset_links'
        verbose_name = '产品资源关联'
        verbose_name_plural = '产品资源关联'
        unique_together = ['product', 'asset']  # 防止重复关联


class Customisation(models.Model):
    """用户定制记录"""
    user_id = models.IntegerField('用户ID')  # 如果使用Django的User模型，可以改为 ForeignKey
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customisations')
    p_size = models.CharField('定制尺寸', max_length=50, blank=True)
    p_finish = models.CharField('定制表面工艺', max_length=50, blank=True)
    p_flex = models.CharField('定制弹性', max_length=50, blank=True)
    p_textures = models.JSONField('定制纹理', default=list, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'customisations'
        verbose_name = '定制记录'
        verbose_name_plural = '定制记录'

    def __str__(self):
        return f"Customisation {self.id} for Product {self.product_id}"


class Cart(models.Model):
    """购物车模型"""
    user_id = models.IntegerField('用户ID')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    design = models.ForeignKey(
        Customisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField('数量', default=1)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'cart'
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['product_id']),
        ]

    def __str__(self):
        return f"Cart {self.id} for User {self.user_id}"

    @property
    def total_price(self):
        """计算小计"""
        return self.quantity * self.unit_price