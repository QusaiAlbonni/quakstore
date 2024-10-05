from io import BytesIO
from PIL import Image

from django.db import models
from django.core.validators import MaxValueValidator
from django.core.files import File
from django.conf import settings
from django.urls import reverse
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category-detail", kwargs={"category_slug": self.slug})


class Discount(models.Model):
    name = models.CharField(max_length=50)

    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[
                                  MaxValueValidator(Decimal(100.0))])
    active = models.BooleanField(default=True)

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(max_length=2047, blank=True, null=True)
    stripe_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    price = models.PositiveBigIntegerField(
        validators=[MaxValueValidator(1000000)])
    stock = models.PositiveIntegerField(validators=[MaxValueValidator(10000)])
    discount = models.ForeignKey(
        Discount, on_delete=models.SET_NULL, null=True, blank=True)
    thumbnail = models.ImageField(
        upload_to='uploads/thumbnails/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date_added',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"category_slug": self.category.slug, "product_slug": self.slug})

    def thumbnail_url(self) -> str | None:
        if self.thumbnail:
            return self.thumbnail.url
        else:
            image = self.images.first()
            if image:
                self.thumbnail = self.make_thumbnail(image.url)
                self.save()

                return self.thumbnail.url
            else:
                return None

    @property
    def in_stock(self) -> bool:
        return bool(self.stock > 0)

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img = img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()

        img.save(thumb_io, 'JPEG', quality=85)
        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class ProductImage(models.Model):
    url = models.ImageField(upload_to='uploads/', blank=True, null=True)
    product = models.ForeignKey(
        to=Product, related_name='images', on_delete=models.CASCADE)
