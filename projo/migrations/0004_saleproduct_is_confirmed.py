# Generated by Django 5.1.3 on 2024-12-05 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projo', '0003_remove_sale_products_alter_sale_sale_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleproduct',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]