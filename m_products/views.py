import os
import uuid
import copy
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, ProductAsset, ProductAssetLink, Customisation
from .serializers import ProductSerializer, ProductAssetSerializer


@api_view(["POST"])
def product_list(request):
    """
    Return list of products with pagination and multi-condition filtering
    Frontend call example:
    getProducts({
        page: 1,
        page_size: 10,
        params: {
            keyword: "Name",
            type: "snowboard",   # corresponds to ProductAsset.type
            min_price: 100,
            max_price: 300,
            p_size: "150",       # can filter by size (substring match)
        }
    })
    """
    data = request.data
    params = data.get("params") or {}

    # ---------- pagination ----------
    page = data.get("page", 1)
    page_size = data.get("page_size", 10)

    # ---------- filtering conditions ----------
    keyword = params.get("keyword")
    asset_type = params.get("type")  # frontend passed asset type
    min_price = params.get("min_price")
    max_price = params.get("max_price")
    p_finish = params.get("p_finish")
    p_size = params.get("p_size")

    # ----------  Basic queryset ----------
    queryset = Product.objects.filter(type=Product.ProductType.SINGLE).order_by("id")

    # ---------- filtering ----------
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

    # remove duplicates caused by joins
    queryset = queryset.distinct()

    # ---------- pagination ----------
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

    # ---------- serialization ----------
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
    Return list of product assets with pagination
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


# create product with linked asset, for single products only, bundles are created separately
@api_view(["POST"])
def add_product(request):

    data = request.data

    print("======== ADD PRODUCT DEBUG START ========")
    print("Incoming data:", data)

    # basic validation
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

            # 1️⃣ search asset
            asset = ProductAsset.objects.get(pk=asset_id)

            print("Found asset:", asset.id)
            print("Asset texture_urls:", asset.texture_urls)

            # 2️⃣ deep copy texture（
            textures_copy = copy.deepcopy(asset.texture_urls or {})
            print("Textures copy:", textures_copy)

            # 3️⃣ create Product (type=1）
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

            # 4️⃣ build link (must succeed)
            link = ProductAssetLink.objects.create(
                product=product,
                asset=asset,
                quantity=1,
            )

            print("Link created:", link.id)

            # 5️⃣ strong link to ensure data integrity, this is a sanity check and should never fail
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
                    },
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


# product status update (for single product, bundles are updated separately)
@api_view(["POST"])
def product_update_status(request):
    """
    update product status (for single products only, bundles are updated separately)
    Request example:
    {
        "id": 1,
        "status": true   # or false
    }
    """
    data = request.data or {}
    product_id = data.get("id")
    status = data.get("status")

    if product_id is None or status is None:
        return Response(
            {"code": 400, "message": "id and status are required"}, status=400
        )

    # status just only boolean 0/1
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
    uploaded with multipart/form-data, field name file or image
    Response: code, data: { path, url, filename }, message
    Upload texture image, save to media/textures/, filename format: texture_YYYYMMDD_HHMMSS_<uuid>.ext
    Request: multipart/form-data, field name file or image
    Response: code, data: { path, url, filename }, message
   
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

    # filename format: texture_YYYYMMDD_HHMMSS_<uuid>.ext
    time_part = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    filename = f"texture_{time_part}_{short_uuid}{ext}"

    # save to media/textures/ 
    textures_dir = os.path.join(settings.MEDIA_ROOT, "textures")
    os.makedirs(textures_dir, exist_ok=True)
    file_path = os.path.join(textures_dir, filename)
    with open(file_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    # elative path (for storage or API response)
    relative_path = f"textures/{filename}"
    # link url to frontend, use /api/media/
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


# Customisation interface
@api_view(["POST"])
def add_design(request):
    """
    create a user customisation record (called when adding to cart)
    Request example:
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

    # ---------- basic validation ----------
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

    # ---------- create customisation record ----------
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
