from .views import stripe_webhook

from django.urls import path

urlpatterns = [
    path('stripe/', stripe_webhook)
]
