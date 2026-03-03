from django.shortcuts import render

# Create your views here.
# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage
from .models import Review
from .serializers import ReviewSerializer
from m_products.models import Product
from rest_framework import status
from m_users.models import UserProfile
from decimal import Decimal


@api_view(["POST"])
def review_list(request):
    """
    返回评论列表（支持分页 + 星级筛选）

    前端调用示例：

    getReviews({
        page: 1,
        page_size: 4,
        params: {
            rating: 5   # 可选，按星级筛选
        }
    })
    """

    data = request.data
    params = data.get("params") or {}

    # ---------- 分页 ----------
    page = data.get("page", 1)
    page_size = data.get("page_size", 4)

    # ---------- 筛选条件 ----------
    rating = params.get("rating")

    # ---------- 基础 queryset ----------
    queryset = Review.objects.select_related("user", "product").order_by("-created_at")

    # ---------- 星级筛选 ----------
    if rating not in [None, ""]:
        try:
            queryset = queryset.filter(rating=int(rating))
        except ValueError:
            return Response(
                {"code": 400, "message": "rating must be an integer"}, status=400
            )

    # ---------- 分页参数校验 ----------
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

    # ---------- 序列化 ----------
    serializer = ReviewSerializer(items, many=True)

    # ---------- 统一返回格式 ----------
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


@api_view(["GET"])
def product_simple_list(request):
    """
    返回所有产品列表（只包含 id 和 name），不分页、不过滤
    """
    products = Product.objects.all().order_by("id").values("id", "name")
    return Response({"code": 200, "message": "ok", "data": list(products)})


@api_view(["POST"])
def add_review(request):
    """
    新增评论接口（只用 user_id，不依赖登录）
    POST 参数示例：
    {
        "user_id": 1,
        "product_id": 5,
        "rating": 4,
        "comment": "Great board!"
    }
    """
    data = request.data

    # ---------- 校验必填 ----------
    required_fields = ["user_id", "product_id", "rating", "comment"]
    for field in required_fields:
        if field not in data or data[field] in [None, ""]:
            return Response(
                {"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST
            )

    # ---------- 获取用户 ----------
    try:
        user = UserProfile.objects.get(pk=int(data["user_id"]))
    except (UserProfile.DoesNotExist, ValueError):
        return Response(
            {"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST
        )

    # ---------- 获取产品 ----------
    try:
        product = Product.objects.get(pk=int(data["product_id"]))
    except (Product.DoesNotExist, ValueError):
        return Response(
            {"error": "Invalid product_id"}, status=status.HTTP_400_BAD_REQUEST
        )

    # ---------- 校验 rating ----------
    try:
        rating = int(data["rating"])
        if rating < 1 or rating > 5:
            raise ValueError()
    except ValueError:
        return Response(
            {"error": "rating must be an integer between 1 and 5"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---------- 创建评论 ----------
    review = Review.objects.create(
        user=user, product=product, rating=rating, comment=data["comment"].strip()
    )

    return Response(
        {
            "code": 200,
            "message": "Review added successfully",
            "data": {
                "id": review.id,
                "user": {"username": user.name},
                "product": {"id": product.id, "name": product.name},
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def review_stats(request):
    """
    返回所有评论统计信息：
    - 每个星级的数量
    - 总评分
    - 平均评分
    """
    # 初始化统计
    rating_counts = {str(i): 0 for i in range(1, 6)}  # 1-5 星
    total_score = 0
    total_reviews = 0

    # 遍历所有评论
    reviews = Review.objects.all()
    for r in reviews:
        score = r.rating
        if 1 <= score <= 5:
            rating_counts[str(score)] += 1
            total_score += score
            total_reviews += 1

    avg_score = total_score / total_reviews if total_reviews else 0

    return Response(
        {
            "code": 200,
            "message": "ok",
            "data": {
                "rating_counts": rating_counts,  # {"1": 3, "2": 5, ...}
                "total_score": total_score,  # 所有评分累加
                "total_reviews": total_reviews,  # 评论总数
                "average_score": round(avg_score, 1),  # 平均评分，保留两位小数
            },
        }
    )


@api_view(["GET"])
def review_summary(request):
    """
    返回评论整体好中坏统计，供管理端饼状图使用
    """
    total = Review.objects.count()
    positive = Review.objects.filter(rating__gte=4).count()
    neutral = Review.objects.filter(rating=3).count()
    negative = Review.objects.filter(rating__lte=2).count()

    if total > 0:
        positive_pct = round((positive / total) * 100)
        neutral_pct = round((neutral / total) * 100)
        negative_pct = round((negative / total) * 100)
    else:
        positive_pct = neutral_pct = negative_pct = 0

    return Response({
        "code": 200,
        "message": "ok",
        "data": {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "total": total,
            # "counts": {
            #     "positive": positive_pct,
            #     "neutral": neutral_pct,
            #     "negative": negative_pct,
            # }
        }
    })