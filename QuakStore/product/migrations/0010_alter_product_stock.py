# Generated by Django 5.1 on 2024-10-08 02:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_product_stripe_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(10000)]),
        ),
    ]
