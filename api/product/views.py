from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from .models import Product, ProductAsset
from .serializers import ProductSerializer, ProductAssetSerializer


@api_view(["POST"])
def product_list(request):
    """
    返回产品列表（支持分页和多条件筛选）
    前端调用示例：
    getProducts({
        page: 1,
        page_size: 4,
        params: {
            keyword: "Name",
            type: "snowboard",   # 对应 ProductAsset.type
            min_price: 100,
            max_price: 300,
            p_finish: "matte",   # 可按板面工艺筛选
            p_size: "150",       # 可按尺寸筛选（匹配包含）
        }
    })
    """
    data = request.data
    params = data.get("params") or {}

    # ---------- 分页 ----------
    page = data.get("page", 1)
    page_size = data.get("page_size", 10)

    # ---------- 筛选条件 ----------
    keyword = params.get("keyword")
    asset_type = params.get("type")  # 前端传的 asset type
    min_price = params.get("min_price")
    max_price = params.get("max_price")
    p_finish = params.get("p_finish")
    p_size = params.get("p_size")

    # ---------- 基础 queryset ----------
    queryset = Product.objects.filter(
        status=True, type=Product.ProductType.SINGLE
    ).order_by("id")

    # ---------- 筛选 ----------
    if keyword:
        queryset = queryset.filter(
            Q(name__icontains=keyword) | Q(p_desc__icontains=keyword)
        )

    if asset_type:
        queryset = queryset.filter(asset_links__asset__type__iexact=asset_type.lower())

    if min_price not in [None, ""]:
        try:
            queryset = queryset.filter(price__gte=float(min_price))
        except ValueError:
            return Response(
                {"code": 400, "message": "min_price must be a number"}, status=400
            )

    if max_price not in [None, ""]:
        try:
            queryset = queryset.filter(price__lte=float(max_price))
        except ValueError:
            return Response(
                {"code": 400, "message": "max_price must be a number"}, status=400
            )

    if p_finish:
        queryset = queryset.filter(p_finish__iexact=p_finish)

    if p_size:
        queryset = queryset.filter(p_size__icontains=p_size)

    # 去重，避免重复
    queryset = queryset.distinct()

    # ---------- 分页处理 ----------
    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return Response(
            {"code": 400, "message": "page and page_size must be integers"}, status=400
        )

    paginator = Paginator(queryset, page_size)
    try:
        page_obj = paginator.page(page)
        items = page_obj.object_list
    except EmptyPage:
        items = []

    # ---------- 序列化返回 ----------
    serializer = ProductSerializer(items, many=True)
    return Response(
        {
            "code": 200,
            "data": {
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
                "list": serializer.data,
            },
            "message": "ok",
        }
    )


@api_view(["POST"])
def product_asset_list(request):
    """
    返回 product_assets 列表（支持分页）
    """
    data = request.data or {}
    page = data.get("page", 1)
    page_size = data.get("page_size", 10)

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return Response(
            {"code": 400, "message": "page and page_size must be integers"},
            status=400,
        )

    queryset = ProductAsset.objects.all().order_by("id")

    paginator = Paginator(queryset, page_size)
    try:
        page_obj = paginator.page(page)
        items = page_obj.object_list
    except EmptyPage:
        items = []

    serializer = ProductAssetSerializer(items, many=True)
    return Response(
        {
            "code": 200,
            "data": {
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
                "list": serializer.data,
            },
            "message": "ok",
        }
    )


@api_view(["POST"])
def product_update_status(request):
    """
    修改单个产品的上架状态
    请求示例:
    {
        "id": 1,
        "status": true   # 或 false
    }
    """
    data = request.data or {}
    product_id = data.get("id")
    status = data.get("status")

    if product_id is None or status is None:
        return Response(
            {"code": 400, "message": "id and status are required"}, status=400
        )

    # status 只能是布尔或 0/1
    if isinstance(status, bool):
        new_status = status
    elif status in [0, 1, "0", "1", "true", "false", "True", "False"]:
        new_status = str(status).lower() in ["1", "true"]
    else:
        return Response(
            {"code": 400, "message": "status must be boolean or 0/1"}, status=400
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"code": 404, "message": "product not found"}, status=404)

    product.status = new_status
    product.save(update_fields=["status"])

    return Response(
        {
            "code": 200,
            "data": {
                "id": product.id,
                "status": product.status,
            },
            "message": "ok",
        }
    )


