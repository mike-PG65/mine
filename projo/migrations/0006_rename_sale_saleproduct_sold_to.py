# Generated by Django 5.1.3 on 2024-12-05 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projo', '0005_saleproduct_sale_products'),
    ]

    operations = [
        migrations.RenameField(
            model_name='saleproduct',
            old_name='sale',
            new_name='sold_to',
        ),
    ]
