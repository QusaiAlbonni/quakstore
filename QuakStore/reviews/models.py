from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from product.models import Product, Category

from decimal import Decimal

User = get_user_model()

# Create your models here.

class Review(models.Model):
    user= models.ForeignKey(User, related_name='reviews', verbose_name=_("User"), on_delete=models.CASCADE)
    product= models.ForeignKey(Product, related_name='reviews', verbose_name=_("Product"), on_delete=models.CASCADE)
    
    rating= models.PositiveSmallIntegerField(_("Rating"), validators=[MaxValueValidator(5), MinValueValidator(1)])
    comment= models.CharField(_("Comment"), max_length=1024)
    
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
      
    class Meta:
        ordering = ('-date_added',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'], name='unique_user_product_review')
        ]
    
    
    def get_absolute_url(self):
        return reverse("reviews-details", kwargs={"category_slug": self.product.category.slug, "product_slug": self.product.slug, "pk": self.pk})