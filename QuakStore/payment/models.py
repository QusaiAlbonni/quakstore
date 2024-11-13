from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

# Create your models here.

User = get_user_model()



class PaymentDetails(models.Model):
    customer_id = models.CharField(max_length=254, unique=True)

    user = models.OneToOneField(
        User, related_name='payment_details', on_delete=models.CASCADE)

    provider = models.CharField(max_length=50, default='stripe')

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    class Status(models.TextChoices):
        PROCESSING = 'processing', 'Processing'
        FAILED = 'failed', 'Failed'
        SUCCESS = 'success', 'Success'
        REFUNDED = 'refunded', 'Refunded'
        UNCONFIRMED= "unconfirmed", "UnConfirmed"

    order = models.ForeignKey(
        Order, related_name='payments', on_delete=models.SET_NULL, null=True)
    payment_method_id = models.CharField(max_length=254)
    amount = models.PositiveBigIntegerField()
    currency = models.CharField(max_length=3)
    description = models.TextField(null=True, blank=True)
    failure_reason = models.CharField(max_length=1023, blank=True, null=True)

    status = models.CharField(max_length=50, choices=Status.choices)

    provider = models.CharField(max_length=50, default='stripe')

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
