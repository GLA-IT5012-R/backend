from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include

urlpatterns = [
    path("hello/", views.hello),
    path("testAuth/", views.testAuth),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("sync-user/", views.sync_user, name="sync-user"),
    path("products/", include("api.product.urls")),
    path("stats-overview/", views.stats_overview, name="stats-overview"),
]
