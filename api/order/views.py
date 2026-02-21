import json
import random
import string
from rest_framework.decorators import api_view
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from .models import Order, OrderItem
from api.product.models import Customisation, Product,ProductAssetLink

@api_view(["POST"])
def admin_order_list(request):
    """
    管理员查询订单接口
    前端传入 JSON：
    {
        "page": 1,
        "page_size": 10,
        "params": {
            "user_id": 1,          # 可选
            "status": "Pending"    # 可选
        }
    }
    返回格式：
    {
        "code": 200,
        "data": {
            "total": 123,
            "page": 1,
            "page_size": 10,
            "list": [
                {
                    "order_id": 1,
                    "order_number": 1,
                    "user_id": 1,
                    "total_price": "199.99",
                    "order_status": "Pending",
                    "address": "xxx",
                    "email": "xxx",
                    "created_at": "2026-02-19T16:00:00Z",
                    "items": [
                        {
                            "order_item_id": 1,
                            "product": {"id": 10, "name": "Snowboard X", "type_id": "SB-001", "is_double_sided": false},
                            "quantity": 2,
                            "unit_price": "99.99",
                            "design": {"id": 7, "p_size":"150", "p_finish":"matte","p_flex":"soft"}
                        },
                        ...
                    ]
                },
                ...
            ]
        }
    }
    """
    try:
        data = request.data
        params = data.get("params") or {}
        page = int(data.get("page", 1))
        page_size = int(data.get("page_size", 10))

        queryset = Order.objects.all().order_by("-created_at")

        # 支持按用户ID筛选
        user_id = params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # 支持按订单状态筛选
        status = params.get("status")
        if status:
            queryset = queryset.filter(order_status=status)

        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = []

        order_list = []
        for order in page_obj:
            items_list = []
            for item in order.items.select_related("design", "product").all():
                # 查询定制信息
                custom_data = None
                if item.design_id:
                    try:
                        custom = Customisation.objects.get(id=item.design_id)
                        custom_data = {
                            "id": custom.id,
                            "p_size": custom.p_size,
                            "p_finish": custom.p_finish,
                            "p_flex": custom.p_flex,
                            "p_textures": custom.p_textures,
                        }
                    except Customisation.DoesNotExist:
                        custom_data = None

                # 查询 product 的 type_id
                type_id = None
                if item.product:
                    link = (
                        ProductAssetLink.objects.filter(product=item.product)
                        .select_related("asset")
                        .first()
                    )
                    if link and link.asset:
                        type_id = link.asset.type_id

                items_list.append({
                    "order_item_id": item.id,
                    "product": {
                        "id": item.product.id if item.product else None,
                        "name": getattr(item.product, "name", None),
                        "type_id": type_id,
                        "is_double_sided": item.product.is_double_sided if item.product else False,
                    } if item.product else None,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "design": custom_data,
                })

            order_list.append({
                "order_id": order.id,
                "order_number": order.order_number,
                "user_id": order.user_id,
                "total_price": str(order.total_price),
                "order_status": order.order_status,
                "address": order.address,
                "email": order.email,
                "created_at": order.created_at.isoformat(),
                "items": items_list,
            })

        return JsonResponse({
            "code": 200,
            "data": {
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
                "list": order_list,
            }
        })
    except Exception as e:
        return JsonResponse({"code": 500, "message": f"Server error: {str(e)}"})
   
@api_view(["POST"])
def add_order(request):
    """
    新增订单接口
    前端传入格式：
    {
        user_id: 1,
        total_price: 199.99,
        order_status: "Pending",
        address:"",
        email:"",
        list: [
            {
                design_id: 1,
                quantity: 2,
                product_id: 10,
                unit_price: 99.99
            },
            {
                design_id: 2,
                product_id: 11,
                quantity: 1,
                unit_price: 199.99
            }
        ]
    }
    """
    try:
        data = json.loads(request.body)

        # 验证必要字段
        required_fields = ["user_id", "total_price", "list"]
        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"code": 400, "message": f"Missing required field: {field}"}
                )

        if not data["list"] or len(data["list"]) == 0:
            return JsonResponse(
                {"code": 400, "message": "Order items list cannot be empty"}
            )

        with transaction.atomic():
            # ---------- 生成唯一 12 位订单号 ----------
            while True:
                prefix = timezone.now().strftime("%Y%m%d")  # 例如 20260221
                suffix = "".join(random.choices(string.digits, k=4))  # 4 位随机数字
                order_number = prefix + suffix
                if not Order.objects.filter(order_number=order_number).exists():
                    break

            # ---------- 创建订单 ----------
            order = Order.objects.create(
                user_id=data["user_id"],
                total_price=data["total_price"],
                order_status=data.get("order_status", "Pending"),
                address=data.get("address", ""),
                email=data.get("email", ""),
                order_number=order_number,
            )

            # ---------- 创建订单项 ----------
            order_items = []
            for item_data in data["list"]:
                if not all(k in item_data for k in ["design_id", "quantity", "unit_price", "product_id"]):
                    raise ValueError("Order item missing required fields")

                try:
                    design = Customisation.objects.get(id=item_data["design_id"])
                except Customisation.DoesNotExist:
                    return JsonResponse({
                        "code": 400,
                        "message": f"Design with id {item_data['design_id']} does not exist",
                    })

                try:
                    product = Product.objects.get(id=item_data["product_id"])
                except Product.DoesNotExist:
                    return JsonResponse({
                        "code": 400,
                        "message": f"Product with id {item_data['product_id']} does not exist",
                    })

                order_items.append(OrderItem(
                    order=order,
                    design=design,
                    product=product,
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                ))

            OrderItem.objects.bulk_create(order_items)

        return JsonResponse({
            "code": 200,
            "data": {
                "order_id": order.id,
                "order_number": order.order_number,
                "message": "Order created successfully"
            },
        })

    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "Invalid JSON format"})
    except ValueError as e:
        return JsonResponse({"code": 400, "message": str(e)})
    except Exception as e:
        return JsonResponse({"code": 500, "message": f"Server error: {str(e)}"})

@api_view(["GET"])
def get_user_orders(request, user_id: int):
    """
    获取指定用户的所有订单及订单项
    URL 示例: /api/orders/user/1/
    """
    try:
        orders = Order.objects.filter(user_id=user_id).order_by("-created_at")
        order_list = []

        for order in orders:
            items_qs = order.items.select_related("design", "product").all()
            items_list = []

            for item in items_qs:
                # 查询完整定制数据
                custom_data = None
                if item.design_id:
                    try:
                        custom = Customisation.objects.get(id=item.design_id)
                        custom_data = {
                            "id": custom.id,
                            "p_size": custom.p_size,
                            "p_finish": custom.p_finish,
                            "p_flex": custom.p_flex,
                            "p_textures": custom.p_textures,
                        }
                    except Customisation.DoesNotExist:
                        custom_data = None

                # 查询 type_id
                type_id = None
                if item.product:
                    link = (
                        ProductAssetLink.objects.filter(product=item.product)
                        .select_related("asset")
                        .first()
                    )
                    if link and link.asset:
                        type_id = link.asset.type_id

                items_list.append(
                    {
                        "order_item_id": item.id,
                        "design": custom_data,
                        "product": (
                            {
                                "id": item.product.id if item.product else None,
                                "name": getattr(item.product, "name", None),
                                "type_id": type_id,
                                "is_double_sided": item.product.is_double_sided,
                            }
                            if item.product
                            else None
                        ),
                        "quantity": item.quantity,
                        "unit_price": str(item.unit_price),
                    }
                )

            order_list.append(
                {
                    "order_id": order.id,
                    "order_number": order.order_number,  # ✅ 新增订单编号
                    "total_price": str(order.total_price),
                    "order_status": order.order_status,
                    "address": order.address,
                    "email": order.email,
                    "created_at": order.created_at.isoformat(),
                    "items": items_list,
                }
            )

        return JsonResponse({"code": 200, "data": order_list})
    except Exception as e:
        return JsonResponse({"code": 500, "message": f"Server error: {str(e)}"})


@api_view(["POST"])
def update_order_status(request):
    """
    更新订单状态接口
    前端传入:
    {
        "order_id": 1,
        "new_status": "Shipped"
    }
    """
    try:
        data = json.loads(request.body)
        order_id = data.get("id")
        new_status = data.get("status")

        if not order_id or not new_status:
            return JsonResponse({"code": 400, "message": "Missing order_id or new_status"})

        # 验证状态值是否有效
        valid_statuses = ["Pending", "Confirmed", "Shipped", "Completed", "Cancelled"]
        if new_status not in valid_statuses:
            return JsonResponse({"code": 400, "message": f"Invalid status: {new_status}"})

        # 使用事务更新
        with transaction.atomic():
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({"code": 404, "message": f"Order {order_id} does not exist"})

            order.order_status = new_status
            order.save()

        return JsonResponse({"code": 200, "data": {"order_id": order.id, "new_status": order.order_status}, "message": "Order status updated successfully"})

    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "Invalid JSON format"})
    except Exception as e:
        return JsonResponse({"code": 500, "message": f"Server error: {str(e)}"})