# Generated by Django 5.1 on 2024-10-05 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_remove_paymentdetails_stripe_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentdetails',
            name='customer_id',
            field=models.CharField(max_length=254, unique=True),
        ),
    ]
