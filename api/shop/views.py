import json
from decimal import Decimal

from django.db import transaction
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, Customisation, Product
from .serializers import CartSerializer


@api_view(["POST"])
def cart_add(request):
    """
    添加商品到购物车
    请求示例：
    {
        "user_id": 10001,
        "product_id": 5,
        "design_id": 12,       # 可选，若传则使用定制记录的价格和配置
        "quantity": 2           # 可选，默认1
    }
    """
    data = request.data
    user_id = data.get("user_id")
    product_id = data.get("product_id")
    design_id = data.get("design_id")
    quantity = data.get("quantity", 1)

    # ---------- 基础校验 ----------
    if not user_id or not product_id:
        return Response(
            {"code": 400, "message": "user_id and product_id are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return Response(
            {"code": 400, "message": "quantity must be a positive integer"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---------- 查询商品 ----------
    try:
        product = Product.objects.get(id=product_id, status=True)
    except Product.DoesNotExist:
        return Response(
            {"code": 404, "message": "Product not found or not available"},
            status=status.HTTP_404_NOT_FOUND,
        )

    unit_price = product.price

    # ---------- 如果传了 design_id，验证并可能覆盖价格 ----------
    design = None
    if design_id:
        try:
            design = Customisation.objects.get(id=design_id, user_id=user_id)
            # 可选：如果定制有单独定价逻辑，可在此调整 unit_price
            # unit_price = design.custom_price  # 假设有 custom_price 字段
        except Customisation.DoesNotExist:
            return Response(
                {"code": 404, "message": "Design not found for this user"},
                status=status.HTTP_404_NOT_FOUND,
            )

    # ---------- 检查是否已存在相同商品+定制 ----------
    existing = Cart.objects.filter(
        user_id=user_id,
        product_id=product_id,
        design_id=design_id,
    ).first()

    if existing:
        # 已存在则累加数量
        existing.quantity += quantity
        existing.save(update_fields=["quantity", "updated_at"])
        cart_item = existing
    else:
        # 新建购物车项
        cart_item = Cart.objects.create(
            user_id=user_id,
            product=product,
            design=design,
            quantity=quantity,
            unit_price=unit_price,
        )

    return Response(
        {
            "code": 200,
            "data": CartSerializer(cart_item).data,
            "message": "Added to cart successfully",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def cart_list(request):
    """
    查询用户的购物车列表（支持分页）
    请求示例：
    {
        "user_id": 10001,
        "page": 1,
        "page_size": 10
    }
    """
    data = request.data
    user_id = data.get("user_id")
    page = data.get("page", 1)
    page_size = data.get("page_size", 10)

    if not user_id:
        return Response(
            {"code": 400, "message": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return Response(
            {"code": 400, "message": "page and page_size must be integers"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    queryset = Cart.objects.filter(user_id=user_id).select_related(
        "product", "design"
    ).order_by("-created_at")

    paginator = Paginator(queryset, page_size)
    try:
        page_obj = paginator.page(page)
        items = page_obj.object_list
    except EmptyPage:
        items = []

    serializer = CartSerializer(items, many=True)

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
def cart_update(request):
    """
    更新购物车项数量
    请求示例：
    {
        "cart_id": 10,
        "quantity": 3
    }
    """
    data = request.data
    cart_id = data.get("cart_id")
    quantity = data.get("quantity")

    if not cart_id or quantity is None:
        return Response(
            {"code": 400, "message": "cart_id and quantity are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return Response(
            {"code": 400, "message": "quantity must be a positive integer"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart_item = get_object_or_404(Cart, id=cart_id)
    cart_item.quantity = quantity
    cart_item.save(update_fields=["quantity", "updated_at"])

    return Response(
        {
            "code": 200,
            "data": CartSerializer(cart_item).data,
            "message": "Cart updated successfully",
        }
    )


@api_view(["POST"])
def cart_remove(request):
    """
    从购物车中移除一项或多项
    请求示例（单条）：
    {
        "cart_id": 10
    }
    或批量：
    {
        "cart_ids": [10, 11, 12]
    }
    """
    data = request.data
    cart_id = data.get("cart_id")
    cart_ids = data.get("cart_ids")

    if not cart_id and not cart_ids:
        return Response(
            {"code": 400, "message": "cart_id or cart_ids is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if cart_id:
        # 单条删除
        cart_item = get_object_or_404(Cart, id=cart_id)
        cart_item.delete()
        return Response(
            {"code": 200, "message": "Cart item removed successfully"},
        )
    else:
        # 批量删除
        if not isinstance(cart_ids, list):
            return Response(
                {"code": 400, "message": "cart_ids must be a list"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted_count, _ = Cart.objects.filter(id__in=cart_ids).delete()
        return Response(
            {
                "code": 200,
                "data": {"deleted_count": deleted_count},
                "message": "Cart items removed successfully",
            }
        )


@api_view(["POST"])
def cart_clear(request):
    """
    清空用户的购物车
    请求示例：
    {
        "user_id": 10001
    }
    """
    user_id = request.data.get("user_id")
    if not user_id:
        return Response(
            {"code": 400, "message": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    deleted_count, _ = Cart.objects.filter(user_id=user_id).delete()
    return Response(
        {
            "code": 200,
            "data": {"deleted_count": deleted_count},
            "message": "Cart cleared successfully",
        }
    )