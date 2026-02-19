from django.db import models
from decimal import Decimal

# 引入 Product 模型
from api.product.models import Product


class Order(models.Model):
    """
    订单主表
    """
    class OrderStatus(models.TextChoices):
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        SHIPPED = 'Shipped'
        COMPLETED = 'Completed'

    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField(help_text="user ID")
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        help_text="order status: Pending/Confirmed/Shipped/Completed"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="total price in pounds, e.g. 199.99"
    )
    
    # ---------- address information ----------
    address = models.TextField(blank=True, help_text="shipping address")
    email = models.EmailField(blank=True, help_text="contact email")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f"Order {self.id} - User {self.user_id}"


class OrderItem(models.Model):
    """
    order item table
    """
    id = models.BigAutoField(primary_key=True)
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="related order"
    )
    
    design = models.ForeignKey(
        'Customisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="related customisation"
    )

    # 新增 product 外键
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="related product"
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="quantity"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="unit price in pounds, e.g. 199.99"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"OrderItem {self.id} - Order {self.order_id}"
