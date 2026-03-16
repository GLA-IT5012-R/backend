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
    retuen list of reviews with pagination and optional rating filter

    Frontend api endpoint: /api/reviews/list/

    getReviews({
        page: 1,
        page_size: 4,
        params: {
            rating: 5   # ranking, optional
        }
    })
    """

    data = request.data
    params = data.get("params") or {}

    # ---------- Pagination ----------
    page = data.get("page", 1)
    page_size = data.get("page_size", 4)

    # ---------- Star Rating Filter ----------
    rating = params.get("rating")

    # ---------- Base queryset ----------
    queryset = Review.objects.select_related("user", "product").order_by("-created_at")

    # ---------- Star Rating Filter ----------
    if rating not in [None, ""]:
        try:
            queryset = queryset.filter(rating=int(rating))
        except ValueError:
            return Response(
                {"code": 400, "message": "rating must be an integer"}, status=400
            )

    # ---------- Pagination Parameter Validation ----------
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

    # ---------- Serialize ----------
    serializer = ReviewSerializer(items, many=True)

    # ---------- Unified Return Format ----------
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
    Return all products with only id and name, no pagination, no filter
    """
    products = Product.objects.all().order_by("id").values("id", "name")
    return Response({"code": 200, "message": "ok", "data": list(products)})


@api_view(["POST"])
def add_review(request):
    """
     create review with user_id, product_id, rating, comment
    POST Form Data:
    {
        "user_id": 1,
        "product_id": 5,
        "rating": 4,
        "comment": "Great board!"
    }
    """
    data = request.data

    # ---------- Check Required Fields ----------
    required_fields = ["user_id", "product_id", "rating", "comment"]
    for field in required_fields:
        if field not in data or data[field] in [None, ""]:
            return Response(
                {"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST
            )

    # ---------- Get user ----------
    try:
        user = UserProfile.objects.get(pk=int(data["user_id"]))
    except (UserProfile.DoesNotExist, ValueError):
        return Response(
            {"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST
        )

    # ---------- Get product ----------
    try:
        product = Product.objects.get(pk=int(data["product_id"]))
    except (Product.DoesNotExist, ValueError):
        return Response(
            {"error": "Invalid product_id"}, status=status.HTTP_400_BAD_REQUEST
        )

    # ---------- Check rating ----------
    try:
        rating = int(data["rating"])
        if rating < 1 or rating > 5:
            raise ValueError()
    except ValueError:
        return Response(
            {"error": "rating must be an integer between 1 and 5"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---------- Create Review ----------
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
     Return overall review statistics:
    - Every rating count
    - Total Score (所有评分累加)
    - Total Reviews
    - Average Rating
    """
    # init counts
    rating_counts = {str(i): 0 for i in range(1, 6)}  # 1-5 星
    total_score = 0
    total_reviews = 0

    # for loop all reviews to calculate counts and totals 
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
                "total_score": total_score,  
                "total_reviews": total_reviews,  
                "average_score": round(avg_score, 1), 
            },
        }
    )


@api_view(["GET"])
def review_summary(request):
    """
    Return overall review summary for admin dashboard pie chart
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