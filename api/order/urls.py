from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_order, name="order-add"),
    path("list/", views.admin_order_list, name="order-list"),
    path("user/<int:user_id>/", views.get_user_orders, name="order-list"),
    path("update-order-status/", views.update_order_status, name="order-update-status/",),
]
