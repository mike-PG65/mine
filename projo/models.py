from django.db import models
from jsonfield import JSONField 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

# class Register(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     username = models.CharField(max_length=50, default='default_username')  # Ensure email is unique
#     email = models.EmailField(max_length=254, unique=True, default='', blank=False)  # Email field
#     password = models.CharField(max_length=128)  # Storing the hashed password

#     def set_password(self, raw_password):
#         # Hash the password before saving
#         self.password = make_password(raw_password)

#     def __str__(self):
#         return f'{self.first_name} {self.last_name}'


class Inventory(models.Model):
    name = models.CharField(max_length=50)  # The name of the item
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Price as a decimal
    stock_location = models.CharField(max_length=128)  # Location where the item is stored (e.g., "Aisle 3, Shelf 2")
    quantity = models.IntegerField(default=0)  # Stock quantity (integer)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    phone = models.CharField(max_length=128)  # Storing phone numbers as strings
    email = models.EmailField(null=True, blank=True)  # Email can be optional

    def __str__(self):
        return f"{self.first_name} {self.last_name}" 


class Sale(models.Model):
    customer_name = models.CharField(max_length=255)
    sale_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Sale #{self.id} - {self.customer_name}"

    def calculate_total_price(self):
        # Calculate the total price based on the related SaleProduct entries
        total = sum(sale_product.total_price for sale_product in self.sale_products.all())
        self.total_price = total
        self.save()


class SaleProduct(models.Model):
    sold_to = models.ForeignKey(Sale, related_name='sale_products', on_delete=models.CASCADE)
    product = models.ForeignKey(Inventory, related_name='sale_products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)
    # sale_products = models.ManyToManyField('SaleProduct', related_name='sales')  # A sale can have multiple products
    

    

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    def save(self, *args, **kwargs):
        # Calculate the total price for this specific product in the sale
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)


# class Sale(models.Model):
#     customer_name = models.CharField(max_length=255)
#     sale_date = models.DateTimeField()
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     products = JSONField(default=list)  # Store list of product quantities here

#     def __str__(self):
#         return f"Sale #{self.id} - {self.customer_name}"

#     def calculate_total_price(self):
#         """
#         Calculate the total price of the sale based on the products and their quantities.
#         """
#         total = 0.00  # Initialize total price
#         for product_data in self.products:
#             product_id = product_data.get('product_id')  # Get product_id from JSON
#             quantity = product_data.get('quantity')  # Get quantity from JSON
#             try:
#                 product = Inventory.objects.get(id=product_id)  # Retrieve product from Inventory
#                 total += product.price * quantity  # Multiply price by quantity and add to total
#             except Inventory.DoesNotExist:
#                 continue  # Skip if the product does not exist (optional: log or raise error)
        
#         self.total_price = total  # Update total price
#         self.save()  # Save the updated sale object
#         return self.total_price





