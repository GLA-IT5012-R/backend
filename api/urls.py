from django.urls import path
from .views import hello  # 引入我们刚写的视图

urlpatterns = [
    path('hello/', hello),
]
