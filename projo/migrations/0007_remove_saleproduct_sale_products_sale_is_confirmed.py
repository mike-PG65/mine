# Generated by Django 5.1.3 on 2024-12-05 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projo', '0006_rename_sale_saleproduct_sold_to'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleproduct',
            name='sale_products',
        ),
        migrations.AddField(
            model_name='sale',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
