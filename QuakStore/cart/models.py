from django.db import models
from django.contrib.auth import get_user_model, get_user
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from product.models import Product
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
User = get_user_model()


class CartItem(models.Model):

    product = models.ForeignKey(Product, verbose_name=_(
        "Product"), on_delete=models.CASCADE, related_name='buyers')
    user = models.ForeignKey(User, verbose_name=_(
        "User"), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        _("Quantity"), validators=[MinValueValidator(1), MaxValueValidator(1000)])

    date_added = models.DateTimeField(_("Date Added"), auto_now=False, auto_now_add=True)
    date_modified = models.DateTimeField(
        _("Date Modified"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product')
        ]
    
    def __str__(self):
        return self.product.name
    
    
