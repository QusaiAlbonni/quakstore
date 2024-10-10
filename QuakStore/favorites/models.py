from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from product.models import Product
# Create your models here.

User = get_user_model()

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', verbose_name=_("User"), on_delete=models.CASCADE)
    product= models.ForeignKey(Product, related_name='favoriters', verbose_name=_("Product"), on_delete=models.CASCADE)
    
    date_added = models.DateTimeField(
        _("Date Modified"),
        auto_now=False,
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _("Date Modified"),
        auto_now=True,
        auto_now_add=False,
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_favorite')
        ]