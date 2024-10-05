from .views import PaymentMethodViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('payment-methods', PaymentMethodViewSet, 'payment-methods')

urlpatterns = [
    
] + router.urls
