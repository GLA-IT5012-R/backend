from django.urls import path
from . import views  # 引入同模块 views

urlpatterns = [
    path('list/', views.product_list, name='product-list'),
]
