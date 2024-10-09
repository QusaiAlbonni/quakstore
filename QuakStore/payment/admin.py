from django.contrib import admin

from .models import Payment, PaymentDetails
# Register your models here.

admin.site.register(Payment)
admin.site.register(PaymentDetails)
