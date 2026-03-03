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
    # user login
    path("request-code/", views.request_verification_code , name="request_verification_code"),
    path("verify-code/", views.verify_verification_code, name="verify_verification_code"),

    # 同步用户信息的URL user
    path("sync-user/", views.sync_user, name="sync-user"),
    path("save-address/", views.save_address, name="save-address"),
    path("stats-overview/", views.stats_overview, name="stats-overview"),
    
]
