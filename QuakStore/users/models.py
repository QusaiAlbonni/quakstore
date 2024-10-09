from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.


class User(AbstractUser):
    items = models.ManyToManyField(
    "product.Product",
    through='cart.CartItem',
    verbose_name=_(""),
    related_name='user',
    through_fields=('user', 'product'))
    email= email = models.EmailField(_("email address"))
    
    def clear_cart(self):
        self.items.remove()
