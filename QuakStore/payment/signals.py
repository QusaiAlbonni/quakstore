
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, PaymentDetails
from .services import StripePaymentService
import stripe

@receiver(post_save, sender=User)
def create_payment_details(sender, instance: User, created: bool):
    if not created:
        return
    payment_service = StripePaymentService()    
    payment_service.create_payment_details(instance)
    