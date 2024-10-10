from django.urls import path, include

from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('products', views.LatestProductsList, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('products/<slug:category_slug>/<slug:product_slug>/',
         views.ProductDetails.as_view(), name='product-detail'),
    path('products/<slug:category_slug>/',
         views.CategoryDetail.as_view(), name='category-detail'),
    path('categories/', views.CategoryList.as_view(), name='category-list')
]
