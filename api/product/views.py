import os
import uuid
import copy
from datetime import datetime
from decimal import Decimal


from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, ProductAsset, ProductAssetLink, Customisation
from .serializers import ProductSerializer, ProductAssetSerializer


@api_view(["POST"])
def product_list(request):
    """
    返回产品列表（支持分页和多条件筛选）
    前端调用示例：
    getProducts({
        page: 1,
        page_size: 10,
        params: {
            keyword: "Name",
            type: "snowboard",   # 对应 ProductAsset.type
            min_price: 100,
            max_price: 300,
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
        type=Product.ProductType.SINGLE
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
def add_product(request):

    data = request.data

    required_fields = ["name", "price", "assets_id"]
    for field in required_fields:
        if not data.get(field):
            return Response(
                {"error": f"{field} is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        with transaction.atomic():

            # 1️⃣ 查 asset
            try:
                asset_id = int(data["assets_id"])
            except (ValueError, TypeError):
                return Response(
                    {"error": "assets_id must be integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            asset = ProductAsset.objects.get(pk=asset_id)

            # 2️⃣ 创建 product
            product = Product.objects.create(
                name=data["name"],
                type=1,  # 强制单品
                price=Decimal(data["price"]),
                status=data.get("status", True),
                p_size=data.get("p_size", ""),
                p_flex=data.get("p_flex", ""),
                p_finish=data.get("p_finish", ""),
                p_desc=data.get("p_desc", ""),
                p_textures=copy.deepcopy(asset.texture_urls or {}),
            )

            # 3️⃣ 建立绑定关系
            ProductAssetLink.objects.create(
                product=product,
                asset=asset,
                quantity=1,
            )

            return Response(
                {"id": product.id, "message": "Product created successfully"},
                status=status.HTTP_201_CREATED,
            )

    except ProductAsset.DoesNotExist:
        return Response(
            {"error": "Asset not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# 新增产品


@api_view(["POST"])
def add_product(request):

    data = request.data

    print("======== ADD PRODUCT DEBUG START ========")
    print("Incoming data:", data)

    # 🔹 基础校验
    if not data.get("name"):
        return Response({"error": "name is required"}, status=400)

    if not data.get("price"):
        return Response({"error": "price is required"}, status=400)

    if not data.get("assets_id"):
        return Response({"error": "assets_id is required"}, status=400)

    try:
        asset_id = int(data["assets_id"])
    except (ValueError, TypeError):
        return Response({"error": "assets_id must be integer"}, status=400)

    try:
        with transaction.atomic():

            # 1️⃣ 查询 asset
            asset = ProductAsset.objects.get(pk=asset_id)

            print("Found asset:", asset.id)
            print("Asset texture_urls:", asset.texture_urls)

            # 2️⃣ 深拷贝 texture（防止引用问题）
            textures_copy = copy.deepcopy(asset.texture_urls or {})
            print("Textures copy:", textures_copy)

            # 3️⃣ 创建 Product（强制单品 type=1）
            product = Product.objects.create(
                name=data["name"],
                type=1,
                price=Decimal(data["price"]),
                status=data.get("status", True),
                p_size=data.get("p_size", ""),
                p_flex=data.get("p_flex", ""),
                p_finish=data.get("p_finish", ""),
                p_desc=data.get("p_desc", ""),
                p_textures=textures_copy,
            )

            print("Product created:", product.id)
            print("Product textures saved:", product.p_textures)

            # 4️⃣ 创建关联（必须成功）
            link = ProductAssetLink.objects.create(
                product=product,
                asset=asset,
                quantity=1,
            )

            print("Link created:", link.id)

            # 5️⃣ 强制验证数据库中是否存在
            link_count = ProductAssetLink.objects.filter(product=product).count()
            print("Link count for product:", link_count)

            print("======== ADD PRODUCT DEBUG END ========")

            return Response(
                {
                    "code": 0,
                    "msg": "success",
                    "data": {
                        "id": product.id,
                        "asset_id": asset.id,
                        "textures": product.p_textures,
                        "link_count": link_count,
                    }
                },
                status=status.HTTP_201_CREATED,
            )

    except ProductAsset.DoesNotExist:
        return Response(
            {"error": "Asset not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    except Exception as e:
        print("ERROR OCCURRED:", str(e))
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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


# Allowed image extensions for texture upload
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


# upload texture and return path/url
@api_view(["POST"])
def upload_texture(request):
    """
    上传图片纹理，保存到 media/textures/，文件名格式：texture_YYYYMMDD_HHMMSS_<uuid>.ext
    请求：multipart/form-data，字段名 file 或 image
    返回：code, data: { path, url, filename }, message
    """
    uploaded_file = request.FILES.get("file") or request.FILES.get("image")
    if not uploaded_file:
        return Response(
            {"code": 400, "message": "No file provided. Use 'file' or 'image'."},
            status=400,
        )

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return Response(
            {
                "code": 400,
                "message": f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
            },
            status=400,
        )

    # 文件名：texture_时间_短uuid.ext
    time_part = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    filename = f"texture_{time_part}_{short_uuid}{ext}"

    # 保存到 media/textures/
    textures_dir = os.path.join(settings.MEDIA_ROOT, "textures")
    os.makedirs(textures_dir, exist_ok=True)
    file_path = os.path.join(textures_dir, filename)
    with open(file_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    # 相对路径（用于存储或 API 返回）
    relative_path = f"textures/{filename}"
    # 访问 URL：项目里用 /api/media/ 提供 media 文件
    url = f"/api/media/{relative_path}"

    return Response(
        {
            "code": 200,
            "data": {
                "path": relative_path,
                "url": url,
                "filename": filename,
            },
            "message": "ok",
        }
    )


# Customisation 相关接口
@api_view(["POST"])
def add_design(request):
    """
    新增一条用户定制记录（加入购物车时调用）
    {
        "product_id": 1,
        "user_id": 10001,
        "p_size": "160",
        "p_finish": "glossy",
        "p_flex": "soft",
        "p_textures": ["tex1.png", "tex2.png"]
    }
    """
    data = request.data

    product_id = data.get("product_id")
    user_id = data.get("user_id")
    p_size = data.get("p_size", "")
    p_finish = data.get("p_finish", "")
    p_flex = data.get("p_flex", "")
    p_textures = data.get("p_textures", [])

    # ---------- 基础校验 ----------
    if not product_id or not user_id:
        return Response(
            {"code": 400, "message": "product_id and user_id are required"},
            status=400,
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"code": 404, "message": "Product not found"},
            status=404,
        )

    # ---------- 创建定制记录 ----------
    customisation = Customisation.objects.create(
        user_id=user_id,
        product=product,
        p_size=p_size,
        p_finish=p_finish,
        p_flex=p_flex,
        p_textures=p_textures,
    )

    return Response(
        {
            "code": 200,
            "data": {
                "id": customisation.id,
                "product_id": product.id,
                "user_id": user_id,
            },
            "message": "Design added successfully",
        }
    )
