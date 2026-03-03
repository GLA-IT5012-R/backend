from django.urls import path
from . import views  # 引入同模块 views

urlpatterns = [
    path("list/", views.product_list, name="product-list"),
    path("assets/", views.product_asset_list, name="product-asset-list"),
    path("add/", views.add_product, name="product-add"),
    path("update-status/", views.product_update_status, name="product-update-status"),
    path("upload/", views.upload_texture, name="product-upload-texture"),
    path("add-design/", views.add_design, name="add_design"),
]
