from django.contrib import admin

from .models import Register, Inventory, Supplier, SaleProduct, Sale

admin.site.register(Register)
admin.site.register(Inventory)
admin.site.register(Supplier)
admin.site.register(Sale)
admin.site.register(SaleProduct)