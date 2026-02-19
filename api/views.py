from django.shortcuts import render
from django.http import JsonResponse
import random
from django.core.mail import send_mail

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
    同步 @clerk 用户信息到数据库，并返回用户信息给前端
    """
    data = request.data
    clerk_id = data.get("id")
    email = data.get("email")
    name = data.get("name")

    if not clerk_id or not email:
        return Response({"error": "Missing required fields"}, status=400)

    # 更新或创建用户
    user, created = UserProfile.objects.update_or_create(
        clerk_id=clerk_id, 
        defaults={
            "email": email,
            "name": name,
            "address": ""  # 默认空
        }
    )

    # 返回完整用户信息给前端存储
    user_data = {
        "id": user.id,
        "clerk_id": user.clerk_id,
        "email": user.email,
        "username": user.name,
        "address": user.address,
    }

    return Response({
        "status": "ok",
        "message": "User synced successfully",
        "data": user_data,
        "created": created
    })


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


@api_view(["POST"])
def request_verification_code(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=400)
    send_verification_code(email)
    return Response({"status": "ok", "message": "Verification code sent"})


@api_view(["POST"])
def verify_verification_code(request):
    email = request.data.get("email")
    code = request.data.get("code")
    if not email or not code:
        return Response({"error": "Email and code required"}, status=400)

    if verify_code(email, code):
        # 创建或更新用户，address 默认空
        from .models import UserProfile
        user, created = UserProfile.objects.get_or_create(
            email=email,
            defaults={
                "name": email,       # 默认用户名为邮箱
                "address": ""        # 默认空地址
            }
        )
        
        # 返回前端需要的用户信息
        return Response({
            "status": "ok",
            "message": "Verification successful",
            "data": {
                "id": user.id,
                "username": user.name,
                "email": user.email,
                "clerk_id": user.clerk_id,
                "address": user.address
            }
        })
    else:
        return Response({"status": "error", "message": "Invalid code"}, status=400)


def send_verification_code(email):
    code = str(random.randint(100000, 999999))  # 6位数字验证码
    # 保存到数据库或缓存
    from django.core.cache import cache

    cache.set(f"verify_{email}", code, timeout=300)  # 5分钟有效
    # 发送邮件
    send_mail(
        subject="Your Verification Code",
        message=f"Your verification code is {code}",
        from_email="no-reply@example.com",
        recipient_list=[email],
    )
    return code


def verify_code(email, code):
    from django.core.cache import cache

    cached_code = cache.get(f"verify_{email}")
    if cached_code == code:
        return True
    return False
