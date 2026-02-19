from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_order, name="order-add"),
    path("user/<int:user_id>/", views.get_user_orders, name="order-list"),
]
