from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator
# Create your models here.

User = get_user_model()

"""
PENDING: The order has been placed but not yet processed.
SHIPPING: The order is on its way to the customer.
SHIPPED: The order has been shipped but not yet delivered.
PROCESSING: The order is being prepared for shipment.
REFUNDED: The order was cancelled or returned, and the payment has been refunded.
PARTIALLY_REFUNDED: Part of the payment for the order has been refunded.
CANCELLED: The order has been cancelled by either the customer or the store.
COMPLETED: The order has been fulfilled and delivered to the customer.
"""


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SHIPPING = 'shipping', 'Shipping'
        SHIPPED = 'shipped', 'Shipped'
        PROCESSING = 'processing', 'Processing'
        REFUNDED = 'refunded', 'Refunded'
        PARTIALLY_REFUNDED = 'partial_refund', 'Partially Refunded'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    owner = models.ForeignKey(User, verbose_name=_(
        "Order"), on_delete=models.CASCADE)

    total = models.PositiveBigIntegerField()
    state = models.CharField(choices=Status.choices, default=Status.PENDING)
    
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    pass
