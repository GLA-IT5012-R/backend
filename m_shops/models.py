from django.db import models
from decimal import Decimal
from m_products.models import Customisation, Product
from m_users.models import UserProfile


class Order(models.Model):
    """
    订单主表
    """

    class OrderStatus(models.TextChoices):
        PENDING = "Pending"
        CONFIRMED = "Confirmed"
        SHIPPED = "Shipped"
        COMPLETED = "Completed"

    id = models.BigAutoField(primary_key=True)
    
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="orders"
    )
    order_number = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        help_text="12-digit unique order number",
    )
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        help_text="order status: Pending/Confirmed/Shipped/Completed",
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="total price in pounds, e.g. 199.99",
    )

    # ---------- address information ----------
    address = models.TextField(blank=True, help_text="shipping address")
    email = models.EmailField(blank=True, help_text="contact email")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_orders"

    def __str__(self):
        return f"Order {self.id} - User {self.user_id}"


class OrderItem(models.Model):
    """
    order item table
    """

    id = models.BigAutoField(primary_key=True)

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", help_text="related order"
    )

    design = models.ForeignKey(
        Customisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        help_text="related customisation",
    )

    # 新增 product 外键
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        help_text="related product",
    )

    quantity = models.PositiveIntegerField(default=1, help_text="quantity")

    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="unit price in pounds, e.g. 199.99"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_order_items"

    def __str__(self):
        return f"OrderItem {self.id} - Order {self.order_id}"


class Cart(models.Model):
    """
    购物车表（每一条记录是一件定制商品）
    """

    id = models.BigAutoField(primary_key=True)

    # -------- 关联用户 --------
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="cart_items"
    )

    # -------- 关联定制记录 --------
    design = models.ForeignKey(
        Customisation,
        on_delete=models.CASCADE,
        related_name="cart_items",
        help_text="用户选择的定制配置",
    )

    # -------- 核心字段 --------
    quantity = models.PositiveIntegerField(default=1, help_text="数量")

    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="单价，例如 199.99"
    )

    # -------- 时间 --------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m_cart"
        ordering = ["-created_at"]
        unique_together = ("user_id", "design")  # 防止同一个用户重复加入同一定制

    def __str__(self):
        return f"CartItem {self.id} - User {self.user_id}"
