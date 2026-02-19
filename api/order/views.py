from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json

from .models import Order, OrderItem
from api.product.models import Customisation


@csrf_exempt
@require_http_methods(["POST"])
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
                product_id:
                unit_price: 99.99
            },
            {
                design_id: 2,
                product_id:
                quantity: 1,
                unit_price: 199.99
            }
        ]
    }
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)

        # 验证必要字段
        required_fields = ["user_id", "total_price", "list"]
        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"code": 400, "message": f"Missing required field: {field}"}
                )

        # 验证订单项列表不为空
        if not data["list"] or len(data["list"]) == 0:
            return JsonResponse(
                {"code": 400, "message": "Order items list cannot be empty"}
            )

        # 使用事务确保数据一致性
        with transaction.atomic():
            # 1. 创建订单
            order = Order.objects.create(
                user_id=data["user_id"],
                total_price=data["total_price"],
                order_status=data.get("order_status", "Pending"),
                address=data.get("address", ""),
                email=data.get("email", ""),
            )

            # 2. 创建订单项
            order_items = []
            for item_data in data["list"]:
                # 验证订单项必要字段
                if not all(
                    k in item_data for k in ["design_id", "quantity", "unit_price"]
                ):
                    raise ValueError("Order item missing required fields")

                # 验证 design_id 是否存在
                try:
                    design = Customisation.objects.get(id=item_data["design_id"])
                except Customisation.DoesNotExist:
                    return JsonResponse(
                        {
                            "code": 400,
                            "message": f"Design with id {item_data['design_id']} does not exist",
                        }
                    )

                # 创建订单项
                order_item = OrderItem(
                    order=order,
                    design=design,
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                )
                order_items.append(order_item)

            # 批量创建订单项
            OrderItem.objects.bulk_create(order_items)

        # 返回成功响应
        return JsonResponse(
            {
                "code": 200,
                "data": {"order_id": order.id, "message": "Order created successfully"},
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "Invalid JSON format"})
    except ValueError as e:
        return JsonResponse({"code": 400, "message": str(e)})
    except Exception as e:
        return JsonResponse({"code": 500, "message": f"Server error: {str(e)}"})
