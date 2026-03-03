from django.urls import path
from . import views

urlpatterns = [
   path("list/", views.review_list, name="review_list"),
   path("products/", views.product_simple_list, name="product_simple_list"),
   path("add/", views.add_review, name="add_review"),
   path("score/",views.review_stats, name="reviews_score"),
   path("summary/",views.review_summary, name="reviews_summary"),
]
