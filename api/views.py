from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .product.models import Product


@api_view(["GET"])
def hello(request):
    return Response({"message": "Hello from Django"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def testAuth(request):
    return Response({"message": f"Hello {request.user.username}"})


@api_view(["POST"])
def sync_user(request):
    """
    同步@clerk用户信息到数据库
    """
    data = request.data
    clerk_id = data.get("id")
    email = data.get("email")
    name = data.get("name")

    if not clerk_id or not email:
        return Response({"error": "Missing required fields"}, status=400)

    user, created = UserProfile.objects.update_or_create(
        clerk_id=clerk_id, defaults={"email": email, "name": name}
    )

    return Response({"status": "ok", "user_id": user.id, "created": created})


@api_view(["GET"])
def stats_overview(request):
    """
    返回基础统计信息：用户数量、产品数量
    """
    user_count = UserProfile.objects.count()
    product_count = Product.objects.count()

    return Response(
        {
            "user_count": user_count,
            "product_count": product_count,
            
        }
    )


