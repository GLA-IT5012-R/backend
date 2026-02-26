from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_order, name="order-add"),
    path("list/", views.admin_order_list, name="order-list"),
    path("user/<int:user_id>/", views.get_user_orders, name="order-list"),
    path("update-order-status/", views.update_order_status, name="order-update-status/",),
    path("add-cart/", views.add_to_cart, name="cart-add"),
    path("cart/<int:user_id>/", views.get_user_cart, name="cart-list"),
    path("updare-cart/<int:cart_item_id>/", views.update_cart_quantity, name="cart-update"),
    path("delcarts/", views.batch_delete_cart, name="cart-batch-delete"),

]
