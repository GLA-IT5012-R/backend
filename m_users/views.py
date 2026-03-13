import random
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import UserProfile
from m_products.models import Product
from m_shops.models import Order


@api_view(["GET"])
def keepalive(request):
    return Response({
        "status": "ok",
        "time": timezone.now()  # 可选，显示当前服务器时间
    })

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
        return Response({"code": 400, "message": "Missing required fields"}, status=400)

    # 查找是否存在
    user = UserProfile.objects.filter(clerk_id=clerk_id).first()

    if user:
        # 只更新 email（避免覆盖用户自己改的昵称）
        user.email = email
        user.save()
        created = False
    else:
        user = UserProfile.objects.create(
            clerk_id=clerk_id,
            email=email,
            name=name,
        )
        created = True

    user_data = {
        "id": user.id,
        "clerk_id": user.clerk_id,
        "email": user.email,
        "username": user.name,
        "address": user.address,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }

    return Response(
        {
            "code": 200,
            "message": "User synced successfully",
            "data": user_data,
            "created": created,
        }
    )

@api_view(["POST"])
def save_address(request):
    clerk_id = request.data.get("clerk_id")
    address = request.data.get("address")

    if not clerk_id:
        return Response(
            {"code": 400, "message": "Missing clerk_id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = UserProfile.objects.filter(clerk_id=clerk_id).first()

    if not user:
        return Response(
            {"code": 404, "message": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    user.address = address
    user.save(update_fields=["address"])  # 🔥 只更新 address 字段

    return Response(
        {
            "code": 200,
            "message": "Address updated successfully",
            "address": user.address,  # 可选，其实可以不返回
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
            defaults={"name": email, "address": ""},  # 默认用户名为邮箱  # 默认空地址
        )

        # 返回前端需要的用户信息
        return Response(
            {
                "status": "ok",
                "message": "Verification successful",
                "data": {
                    "id": user.id,
                    "username": user.name,
                    "email": user.email,
                    "clerk_id": user.clerk_id,
                    "address": user.address,
                },
            }
        )
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


@api_view(["GET"])
def stats_overview(request):
    """
    返回基础统计信息：用户数量、产品数量、订单数量
    """
    user_count = UserProfile.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()

    data = {
        "user_count": user_count,
        "product_count": product_count,
        "order_count": order_count
    }

    return Response({
        "code": 200,
        "message": "统计信息获取成功",
        "data": data
    })
