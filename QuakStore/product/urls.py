from django.urls import path, include

from product import views

urlpatterns = [
    path('products/', views.LatestProductsList.as_view()),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.ProductDetails.as_view(), name='product-detail'),
    path('products/<slug:category_slug>/', views.CategoryDetail.as_view(), name='category-detail')
]
