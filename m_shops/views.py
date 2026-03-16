import json
import random
import string
from rest_framework.decorators import api_view
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from .models import Order, OrderItem, Cart
from m_products.models import Customisation, Product, ProductAssetLink
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
def admin_order_list(request):
    """
     admin order list API
    Request body example:
    {
        "page": 1,
        "page_size": 10,
        "params": {
            "user_id": 1,          # optional filter by user ID
            "status": "Pending"    # optional filter by order status (Pending, Confirmed, Shipped, Completed, Cancelled)
        }
    }
    response example:
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
                            "product": {"id": 10, "name": "Snowboard X", "asset_code": "SB-001", "is_double_sided": false},
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

        # support filter by user ID
        user_id = params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # support filter by order status
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
                #  search for customisation details
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

                #  search for product's asset_code
                asset_code = None
                if item.product:
                    link = (
                        ProductAssetLink.objects.filter(product=item.product)
                        .select_related("asset")
                        .first()
                    )
                    if link and link.asset:
                        asset_code = link.asset.asset_code

                items_list.append(
                    {
                        "order_item_id": item.id,
                        "product": (
                            {
                                "id": item.product.id if item.product else None,
                                "name": getattr(item.product, "name", None),
                                "asset_code": asset_code,
                                "is_double_sided": (
                                    item.product.is_double_sided
                                    if item.product
                                    else False
                                ),
                            }
                            if item.product
                            else None
                        ),
                        "quantity": item.quantity,
                        "unit_price": str(item.unit_price),
                        "design": custom_data,
                    }
                )

            order_list.append(
                {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "user_id": order.user_id,
                    "total_price": str(order.total_price),
                    "order_status": order.order_status,
                    "address": order.address,
                    "email": order.email,
                    "created_at": order.created_at.isoformat(),
                    "items": items_list,
                }
            )

        return JsonResponse(
            {
                "code": 200,
                "data": {
                    "total": paginator.count,
                    "page": page,
                    "page_size": page_size,
                    "list": order_list,
                },
            }
        )
    except Exception as e:
        return JsonResponse({"code": 500, "message": f"Server error: {str(e)}"})


@api_view(["POST"])
def add_order(request):
    """
    create order API
    Request body example:
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

        # verify required fields
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
            # ---------- create unique 12-digit order number ----------
            while True:
                prefix = timezone.now().strftime("%Y%m%d")  # 例如 20260221
                suffix = "".join(random.choices(string.digits, k=4))  # 4 位随机数字
                order_number = prefix + suffix
                if not Order.objects.filter(order_number=order_number).exists():
                    break

            # ---------- create order ----------
            order = Order.objects.create(
                user_id=data["user_id"],
                total_price=data["total_price"],
                order_status=data.get("order_status", "Pending"),
                address=data.get("address", ""),
                email=data.get("email", ""),
                order_number=order_number,
            )

            # ---------- create order items ----------
            order_items = []
            for item_data in data["list"]:
                if not all(
                    k in item_data
                    for k in ["design_id", "quantity", "unit_price", "product_id"]
                ):
                    raise ValueError("Order item missing required fields")

                try:
                    design = Customisation.objects.get(id=item_data["design_id"])
                except Customisation.DoesNotExist:
                    return JsonResponse(
                        {
                            "code": 400,
                            "message": f"Design with id {item_data['design_id']} does not exist",
                        }
                    )

                try:
                    product = Product.objects.get(id=item_data["product_id"])
                except Product.DoesNotExist:
                    return JsonResponse(
                        {
                            "code": 400,
                            "message": f"Product with id {item_data['product_id']} does not exist",
                        }
                    )

                order_items.append(
                    OrderItem(
                        order=order,
                        design=design,
                        product=product,
                        quantity=item_data["quantity"],
                        unit_price=item_data["unit_price"],
                    )
                )

            OrderItem.objects.bulk_create(order_items)

        return JsonResponse(
            {
                "code": 200,
                "data": {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "message": "Order created successfully",
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "Invalid JSON format"})
    except ValueError as e:
        return JsonResponse({"code": 400, "message": str(e)})
    except Exception as e:
        return JsonResponse({"code": 500, "message": f"Server error: {str(e)}"})


@api_view(["GET"])
def get_user_orders(request, user_id: int):
    """
    get user orders API and order details API
    URL example: /api/orders/user/1/
    """
    try:
        orders = Order.objects.filter(user_id=user_id).order_by("-created_at")
        order_list = []

        for order in orders:
            items_qs = order.items.select_related("design", "product").all()
            items_list = []

            for item in items_qs:
                #  srearch for full customisation data
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

                #  search for asset_code
                asset_code = None
                if item.product:
                    link = (
                        ProductAssetLink.objects.filter(product=item.product)
                        .select_related("asset")
                        .first()
                    )
                    if link and link.asset:
                        asset_code = link.asset.asset_code

                items_list.append(
                    {
                        "order_item_id": item.id,
                        "design": custom_data,
                        "product": (
                            {
                                "id": item.product.id if item.product else None,
                                "name": getattr(item.product, "name", None),
                                "asset_code": asset_code,
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
                    "order_number": order.order_number,  # ✅ create order number in order model and return it in API
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
    update order status API
    Request body example:
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
            return JsonResponse(
                {"code": 400, "message": "Missing order_id or new_status"}
            )

        # verify new_status is valid
        valid_statuses = ["Pending", "Confirmed", "Shipped", "Completed", "Cancelled"]
        if new_status not in valid_statuses:
            return JsonResponse(
                {"code": 400, "message": f"Invalid status: {new_status}"}
            )

        # use transaction to ensure data integrity
        with transaction.atomic():
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return JsonResponse(
                    {"code": 404, "message": f"Order {order_id} does not exist"}
                )

            order.order_status = new_status
            order.save()

        return JsonResponse(
            {
                "code": 200,
                "data": {"order_id": order.id, "new_status": order.order_status},
                "message": "Order status updated successfully",
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "Invalid JSON format"})
    except Exception as e:
        return JsonResponse({"code": 500, "message": f"Server error: {str(e)}"})


@api_view(["POST"])
def add_to_cart(request):
    """
    添加购物车接口 create cart API
    Request body example:
    {
        "user_id": 1,
        "design_id": 3,
        "quantity": 1,
        "unit_price": 199.99
    }
    """
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        design_id = data.get("design_id")
        quantity = int(data.get("quantity", 1))
        unit_price = data.get("unit_price")

        if not user_id or not design_id or not unit_price:
            return JsonResponse({"code": 400, "message": "Missing required fields"})

        with transaction.atomic():

            try:
                design = Customisation.objects.get(id=design_id)
            except Customisation.DoesNotExist:
                return JsonResponse({"code": 404, "message": "Customisation not found"})

            cart_item, created = Cart.objects.get_or_create(
                user_id=user_id,
                design=design,
                defaults={
                    "quantity": quantity,
                    "unit_price": unit_price,
                },
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        return JsonResponse(
            {
                "code": 200,
                "data": {
                    "cart_item_id": cart_item.id,
                    "quantity": cart_item.quantity,
                },
                "message": "Added to cart successfully",
            }
        )

    except Exception as e:
        return JsonResponse({"code": 500, "message": str(e)})


@api_view(["GET"])
def get_user_cart(request, user_id: int):
    """
    get user cart API
    URL example: /api/cart/user/1/
    """
    try:
        cart_items = (
            Cart.objects.filter(user_id=user_id)
            .select_related("design", "design__product")
            .order_by("-created_at")
        )

        cart_list = []

        for item in cart_items:
            design = item.design
            product = design.product if hasattr(design, "product") else None

            # search for asset_code ,same as previous ones in order items, can consider refactor to a utility function if needed
            asset_code = None
            if product:
                link = (
                    ProductAssetLink.objects.filter(product=product)
                    .select_related("asset")
                    .first()
                )
                if link and link.asset:
                    asset_code = link.asset.asset_code

            cart_list.append(
                {
                    "cart_item_id": item.id,
                    "design": {
                        "id": design.id,
                        "p_size": design.p_size,
                        "p_finish": design.p_finish,
                        "p_flex": design.p_flex,
                        "p_textures": design.p_textures,
                    },
                    "product": (
                        {
                            "id": product.id,
                            "name": product.name,
                            "asset_code": asset_code,
                            "is_double_sided": product.is_double_sided,
                        }
                        if product
                        else None
                    ),
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "created_at": item.created_at.isoformat(),
                }
            )

        return JsonResponse({"code": 200, "data": cart_list})

    except Exception as e:
        return JsonResponse({"code": 500, "message": str(e)})


@api_view(["PATCH"])
def update_cart_quantity(request, cart_item_id: int):
    """
     update cart quantity API
    Request body example:
    {
        "quantity": 3
    }
    """
    try:
        data = json.loads(request.body)
        quantity = data.get("quantity")

        if not quantity or int(quantity) < 1:
            return JsonResponse({"code": 400, "message": "Quantity must be >= 1"})

        try:
            cart_item = Cart.objects.get(id=cart_item_id)
        except Cart.DoesNotExist:
            return JsonResponse({"code": 404, "message": "Cart item not found"})

        cart_item.quantity = int(quantity)
        cart_item.save()

        return JsonResponse(
            {
                "code": 200,
                "data": {
                    "cart_item_id": cart_item.id,
                    "quantity": cart_item.quantity,
                },
                "message": "Quantity updated successfully",
            }
        )

    except Exception as e:
        return JsonResponse({"code": 500, "message": str(e)})


@api_view(["DELETE"])
def batch_delete_cart(request):
    """
    batch delete cart items with safe delete for Customisation
    """
    try:
        data = json.loads(request.body)
        ids = data.get("cart_item_ids", [])

        if not ids:
            return JsonResponse({"code": 400, "message": "No cart_item_ids provided"})

        with transaction.atomic():

            cart_items = Cart.objects.filter(id__in=ids).select_related("design")

            # collect design IDs to check if they can be safely deleted after cart items are deleted
            design_to_check = set()
            for item in cart_items:
                if item.design:
                    design_to_check.add(item.design.id)

            # del Cart
            cart_items.delete()

            # del design
            for design_id in design_to_check:
                try:
                    design = Customisation.objects.get(id=design_id)
                    cart_ref_count = Cart.objects.filter(design=design).count()
                    order_ref_count = OrderItem.objects.filter(design=design).count()
                    if cart_ref_count == 0 and order_ref_count == 0:
                        design.delete()
                except Customisation.DoesNotExist:
                    continue

        return JsonResponse({"code": 200, "message": "Batch delete successful"})

    except Exception as e:
        return JsonResponse({"code": 500, "message": str(e)})


@api_view(["GET"])
def monthly_order_count(request):
    """
    return monthly order count for current year
    """
    try:
        current_year = now().year
        #  by month aggregation of order count
        monthly_counts = (
            Order.objects
            .filter(created_at__year=current_year)
            .annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(order_count=Count('id'))
            .order_by('month')
        )

        #  result with all 12 months having values
        result = {month: 0 for month in range(1, 13)}
        for entry in monthly_counts:
            result[entry['month']] = entry['order_count']

        return Response(
            {"code": 200, "msg": "success", "data": result},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"code": 500, "msg": f"error: {str(e)}", "data": {}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )