from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_order, name='add_order'),
    path("list/", views.admin_order_list, name="order-list"),
    path("user/<int:user_id>/", views.get_user_orders, name="order-list"),
    path("update-order-status/", views.update_order_status, name="order-update-status/"),
    path("add-cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/<int:user_id>/", views.get_user_cart, name="cart-list"),
    path("updare-cart/<int:cart_item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("delcarts/", views.batch_delete_cart, name="batch_delete_cart"),
    path("month-sales/", views.monthly_order_count, name="monthly-order-ount"),
]
    