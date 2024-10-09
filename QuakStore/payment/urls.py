from .views import PaymentMethodViewSet, stripe_webhook

from django.urls import path, include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('payment-methods', PaymentMethodViewSet, 'payment-methods')

urlpatterns = [
    
    path(
        'payment/methods/',
        PaymentMethodViewSet.as_view(
            {
                'post': 'create',
                'get': 'list',
                'delete': 'destroy'
            }
        ),
        name='payment-method'
    )
    
]
