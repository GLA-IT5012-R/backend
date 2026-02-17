from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include

urlpatterns = [
    path("hello/", views.hello),
    path("testAuth/", views.testAuth),
    # JWT认证相关的URL. admin
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 同步用户信息的URL user
    path("sync-user/", views.sync_user, name="sync-user"),
    path("stats-overview/", views.stats_overview, name="stats-overview"),

    # 产品相关的URL product
    path("products/", include("api.product.urls")),
    #订单的URL
    path("orders/", include("api.order.urls")),
]
