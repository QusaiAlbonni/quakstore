from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet

router = DefaultRouter()

router.register('items', CartItemViewSet, basename='cartitems')

urlpatterns = [
    path('cart/', include(router.urls))
]
