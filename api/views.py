from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .models import Product
from .serializers import ProductSerializer
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer

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


@api_view(["POST"])
def product_list(request):
    """
    返回产品列表（支持分页和多条件筛选）
    前端调用示例：
    getProducts({
        page: 1,
        page_size: 4,
        params: {
            keyword: "Burton",
            min_price: 100,
            max_price: 300,
            p_finish: "matte",    # 新增: 可按材质筛选
            p_size: "150",        # 可按尺寸筛选（可匹配包含的尺寸）
        }
    })
    """
    data = request.data
    queryset = Product.objects.filter(type=1).order_by("id")  # 仅单品，可改为 type 参数灵活筛选

    # ---------- 获取分页 ----------
    page = data.get("page", 1)
    page_size = data.get("page_size", 10)

    # ---------- 获取筛选条件 ----------
    params = data.get("params") or {}
    keyword = params.get("keyword")
    min_price = params.get("min_price")
    max_price = params.get("max_price")
    p_finish = params.get("p_finish")
    p_size = params.get("p_size")

    # ---------- 筛选 ----------
    if keyword:
        queryset = queryset.filter(
            Q(name__icontains=keyword) |
            Q(p_desc__icontains=keyword)
        )

    if min_price not in [None, ""]:
        try:
            queryset = queryset.filter(price__gte=float(min_price))
        except ValueError:
            return Response({"code": 400, "message": "min_price must be a number"}, status=400)

    if max_price not in [None, ""]:
        try:
            queryset = queryset.filter(price__lte=float(max_price))
        except ValueError:
            return Response({"code": 400, "message": "max_price must be a number"}, status=400)

    if p_finish:
        queryset = queryset.filter(p_finish__iexact=p_finish)

    if p_size:
        # 假设 p_size 是一个范围字符串，如 "140,150,160"，前端传单个尺寸可做包含匹配
        queryset = queryset.filter(p_size__icontains=p_size)

    # ---------- 分页 ----------
    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return Response({"code": 400, "message": "page and page_size must be integers"}, status=400)

    paginator = Paginator(queryset, page_size)
    try:
        page_obj = paginator.page(page)
        items = page_obj.object_list
    except EmptyPage:
        items = []

    # ---------- 序列化返回 ----------
    serializer = ProductSerializer(items, many=True)
    return Response({
        "code": 200,
        "data": {
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "list": serializer.data,
        },
        "message": "ok"
    })