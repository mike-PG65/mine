from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import Inventory
from django.contrib.auth.decorators import login_required
from . models import Register
import re
import json
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from .models import Supplier, Sale, SaleProduct
from weasyprint import HTML
from django.db import transaction


# from django.contrib.auth import update_session_auth_hash
# from .forms import InventoryForm


# login register urls


def register(request):
    if request.method == 'POST':
        # Get the data from the POST request
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']  # New email field
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # First Name and Last Name Validation (letters only)
        if not re.match(r'^[a-zA-Z\s]*$', first_name):
            messages.error(request, "First Name should only contain letters.")
            return redirect(request.path)  # Re-render the form with the error message

        if not re.match(r'^[a-zA-Z\s]+$', last_name):
            messages.error(request, "Last Name should only contain letters.")
            return redirect(request.path)  # Re-render the form with the error message

        # Email Validation (simple check for format)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, "Please enter a valid email address.")
            return redirect(request.path)

        # Check if the email already exists
        if get_user_model().objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please choose another one.")
            return redirect(request.path)

        # Check if the username already exists
        if get_user_model().objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
            return redirect(request.path)

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Password and Confirm Password do not match.")
            return redirect(request.path)  # Re-render the form with the error message

        # Additional password strength check (optional)
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect(request.path)

        # Create the user if all checks pass
        user = get_user_model()
        new_user = user(first_name=first_name, last_name=last_name, username=username, email=email)
        new_user.password = make_password(password)  # Hash the password before saving
        new_user.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')  # Redirect to the login page after successful registration

    return render(request, 'register.html')

def login(request):
    if request.user.is_authenticated:
        logout(request)  # Log out the current user before allowing login again (optional)

    # Get the 'next' parameter to redirect to the requested page after login
    next_page = request.GET.get('next', 'home')  # Default to 'home' if no next is specified

    # Make sure 'next' is an internal path to prevent open redirects
    if not next_page.startswith('/'):
        next_page = 'home'  # Default to home if the 'next' is not a valid internal path

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user by searching for a user with the provided username and password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # Log the user in
            messages.success(request, "Login successful!")  # Display a success message
            return redirect(next_page)  # Redirect to the page the user wanted to visit or home

        else:
            # If authentication fails, render the login page with an error message
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, 'registration/login.html')  # Make sure this points to the correct path

    # If GET request, render the login page
    return render(request, 'registration/login.html')  # Ensure the path is correct here as well

@login_required
def edit_profile(request):
    # Get the user's profile based on the logged-in user (using the built-in User model)
    user = request.user  # This is the authenticated user

    if request.method == 'POST':
        # Get the new values from the form submission
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Update the profile fields with the new values
        user.first_name = first_name
        user.last_name = last_name
        user.username = username  # Update the username

        if password:  # If a new password is provided, hash and save it
            user.password = make_password(password)

        # Save the updated user profile
        user.save()

        # Show a success message
        messages.success(request, "Your profile has been updated successfully.")
        
        # Redirect to the same page to see the updated profile
        return redirect('edit_profile')  # Redirect to avoid form resubmission on refresh

    # If the method is GET, just display the profile data in a form
    return render(request, 'edit_profile.html', {'profile': user})

# def create_user_profile(user):
#     if not hasattr(user, 'register'):
#         profile = Register(user=user, first_name=user.first_name, last_name=user.last_name)
#         profile.save()    



def logout(request):
    print(request.user.is_authenticated)  # Debugging: Check if the user is authenticated
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')



def index(request):
    return render(request, 'index.html')


    #inventory urls


def add_inventory(request, pk=None):
    if pk:
        item = get_object_or_404(Inventory, pk=pk)
    else:
        item = None

    if request.method == 'POST':
        name = request.POST.get('name')
        stock_location = request.POST.get('stock_location')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')

        # Check if all fields are filled
        if not name or not stock_location or not quantity or not price:
            messages.error(request, "All fields are required.")
            return redirect(request.path)  

        # Validate that the name contains only letters (no numbers or special characters)
        if not re.match(r'^[a-zA-Z\s]*$', name):
            messages.error(request, "Name should only contain letters and spaces.")
            return redirect(request.path)  # Re-render the form with the error message

        # Validate that price and quantity are positive numbers
        if not quantity.isdigit() or int(quantity) <= 0:
            messages.error(request, "Quantity should not be a negative number or 0.")
            return redirect(request.path)  # Re-render the form with the error message

        if not price.replace('.', '', 1).isdigit() or float(price) <= 0:
            messages.error(request, "Price should not be a negative number or 0.")
            return redirect(request.path)  # Re-render the form with the error message

        # Convert to appropriate data types
        quantity = int(quantity)
        price = float(price)

        # Check if the item already exists (based on the name or another unique field)
        existing_item = Inventory.objects.filter(name__iexact=name).first()

        if existing_item:
            # Display a message that the item already exists
            messages.error(request, f'Item "{name}" already exists in the inventory.')
            return redirect(request.path)  # Re-render the form with the error message

        if item:
            # If an item is being edited, replace the current quantity with the new one
            item.name = name
            item.stock_location = stock_location  # Keep stock location updated if needed
            item.quantity = quantity  # Replace the existing quantity with the new quantity
            item.price = price
            item.save()

            messages.success(request, f'{item.name} updated successfully.')

        else:
            # Add a new item if it's not being edited
            Inventory.objects.create(
                name=name,
                stock_location=stock_location,
                quantity=quantity,
                price=price
            )
            messages.success(request, 'Item added successfully.')

        return redirect('inventory_list')  # Redirect to the inventory list page.

    # Show existing item data when editing or adding an existing item
    return render(request, 'add_inventory.html', {'item': item})



def inventory_list(request):
    """View to list all inventory items."""
    items = Inventory.objects.all()  # Get all inventory items
    return render(request, 'inventory_list.html', {'items': items})


# def delete_inventory(request, pk):
#     # Get the inventory item by its primary key (ID)
#     item = get_object_or_404(Inventory, pk=pk)

#     if request.method == 'POST':
#         # If POST request, delete the item from the database
#         item.delete()
#         # Add a success message to notify the user
#         messages.success(request, f'{item.name} has been deleted successfully.')
#         # Redirect to the inventory list page after deletion
#         return redirect('inventory_list')

#     # If it's a GET request, just show the delete confirmation
#     return render(request, 'delete_inventory.html', {'item': item})


# def delete_inventory(request, inventory_id):
#     # Get the Inventory item
#     inventory_item = get_object_or_404(Inventory, id=inventory_id)

#     # Check if the request method is POST (i.e., the user confirmed deletion)
#     if request.method == 'POST':
#         inventory_item.delete()  # Delete the Inventory item
#         return redirect('inventory_list')  # Redirect to the inventory list page

#     # Render the delete confirmation template
#     return render(request, 'delete.html', {
#         'object_type': 'inventory',  # Pass 'inventory' as the object type
#         'object': inventory_item  # Pass the inventory item (optional, for display purposes)
#     })


#delete url

def delete(request, pk, object_type):
    if object_type == 'sale':
        # Delete a Sale
        sale = get_object_or_404(Sale, id=pk)

        if request.method == 'POST':
            sale.delete()  # Delete the Sale
            messages.success(request, f"Sale #{sale.id} deleted successfully.")
            return redirect('sale_list')  # Redirect to the sales list page

        # Render the delete confirmation template for sale
        return render(request, 'delete.html', {
            'object_type': 'sale',
            'object': sale,
        })

    elif object_type == 'inventory':
        # Delete an Inventory item
        item = get_object_or_404(Inventory, id=pk)

        if request.method == 'POST':
            item.delete()  # Delete the Inventory item
            messages.success(request, f"Item {item.name} deleted successfully.")
            return redirect('inventory_list')  # Redirect to the inventory list page

        # Render the delete confirmation template for inventory
        return render(request, 'delete.html', {
            'object_type': 'inventory',
            'object': item,
        })

    elif object_type == 'supplier':
        # Delete a Supplier
        supplier = get_object_or_404(Supplier, id=pk)

        if request.method == 'POST':
            supplier.delete()  # Delete the Supplier
            messages.success(request, f"Supplier {supplier.first_name} {supplier.last_name} deleted successfully.")
            return redirect('supplier_list')  # Redirect to the supplier list page

        # Render the delete confirmation template for supplier
        return render(request, 'delete.html', {
            'object_type': 'supplier',
            'object': supplier,
        })

    else:
        # Invalid object type (either 'sale' or 'inventory' should be passed)
        messages.error(request, "Invalid object type.")
        return redirect('home')  # Redirect to a safe page
        


#supplier url

def add_supplier(request, pk=None):
    # If pk is provided, we are editing an existing supplier
    if pk:
        supplier = get_object_or_404(Supplier, pk=pk)
    else:
        supplier = None

    # Fetch all products from the Inventory model
    products = Inventory.objects.all()  # Get all inventory items (products)

    if request.method == 'POST':
        # Get data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        product_id = request.POST.get('product')  # Get the selected product ID
        phone = request.POST.get('phone')
        email = request.POST.get('email')  # Email is optional

        # Check if all required fields are filled
        if not first_name or not last_name or not product_id or not phone:
            messages.error(request, "First Name, Last Name, Product, and Phone are required fields.")
            return redirect(request.path)

        # Validate first and last names to contain only letters
        if not re.match(r'^[a-zA-Z\s]*$', first_name):
            messages.error(request, "First Name should only contain letters.")
            return redirect(request.path)

        if not re.match(r'^[a-zA-Z\s]+$', last_name):
            messages.error(request, "Last Name should only contain letters.")
            return redirect(request.path)

        # Validate phone number to ensure it's between 10 and 13 digits
        if not re.match(r'^\d{10,13}$', phone):
            messages.error(request, "Phone number must contain between 10 and 13 digits.")
            return redirect(request.path)

        # Check if the selected product exists in the inventory
        try:
            product = Inventory.objects.get(id=product_id)
        except Inventory.DoesNotExist:
            messages.error(request, "Selected product does not exist.")
            return redirect(request.path)

        # If editing an existing supplier
        if supplier:
            supplier.first_name = first_name
            supplier.last_name = last_name
            supplier.product = product  # Assign the product object (not just the ID)
            supplier.phone = phone
            supplier.email = email  # Email is optional, can be left blank
            supplier.save()  # Save the updated supplier
            messages.success(request, f'Supplier {supplier.first_name} {supplier.last_name} updated successfully.')
        else:
            # If adding a new supplier
            Supplier.objects.create(
                first_name=first_name,
                last_name=last_name,
                product=product,  # Assign the product object
                phone=phone,
                email=email  # Email is optional
            )
            messages.success(request, 'Supplier added successfully.')

        return redirect('supplier_list')  # Redirect to the list of suppliers after saving.

    return render(request, 'add_supplier.html', {'supplier': supplier, 'products': products})


def supplier_list(request):
    suppliers = Supplier.objects.all()  # Get all suppliers
    return render(request, 'supplier_list.html', {'suppliers': suppliers})





def search_inventory(request):
    search_query = request.GET.get('search_query', '').lower()  # Get the search query from the GET request

    # Filter the inventory items that start with the search query
    if search_query:
        inventory_items = Inventory.objects.filter(name__icontains=search_query)  # Search for products containing the query

        # Prepare the response data
        inventory_data = [
            {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'quantity': item.quantity,
            }
            for item in inventory_items
        ]

        # Return the data as JSON
        return JsonResponse({'inventory': inventory_data})
    else:
        return JsonResponse({'message': 'No products found.'}, status=404)

def update_stock(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        try:
            # Retrieve the product from the database
            product = Inventory.objects.get(id=product_id)
            # Update the stock by subtracting the selected quantity
            if product.quantity >= quantity:
                product.quantity -= quantity
                product.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Not enough stock available.'})
        except Inventory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})




# def add_sale(request, sale_id=None):
#     # Handle the case where sale_id is provided and fetch the sale or create a new one if not found
#     sale = None
#     if sale_id:
#         try:
#             sale = Sale.objects.get(id=sale_id)
#         except Sale.DoesNotExist:
#             sale = None  # If sale doesn't exist, create a new one

#     if request.method == 'POST':
#         # Get customer name and sale date from the form
#         customer_name = request.POST.get('customer_name')
#         sale_date = request.POST.get('sale_date')

#         # Handle JSON data sent from the form for the products
#         products_str = request.POST.get('products')  # Get the 'products' field from the request

#         # Debugging: Print out the raw product data
#         print(f"Raw products data from POST: {products_str}")  # Add this to debug

#         if not products_str:
#             messages.error(request, "No products data provided.")
#             return redirect('add_sale')

#         try:
#             # If products_str is a valid JSON string, parse it into a list
#             products_data = json.loads(products_str)
#             print(f"Parsed products data: {products_data} (type: {type(products_data)})")  # Debugging
#         except (json.JSONDecodeError, TypeError) as e:
#             print(f"Error parsing JSON: {e}")  # Debugging
#             messages.error(request, "Error processing products data.")
#             return redirect('add_sale')

#         # Validate that products_data is a list and contains items
#         if not isinstance(products_data, list) or not products_data:
#             messages.error(request, "Invalid products data. Ensure the products are in a list format.")
#             return redirect('add_sale')

#         # Validate each item in products_data to make sure it has 'product_id' and 'quantity'
#         for item in products_data:
#             if not isinstance(item, dict):
#                 messages.error(request, "Each product should be a dictionary with 'product_id' and 'quantity'.")
#                 return redirect('add_sale')
#             product_id = item.get('product_id')
#             quantity = item.get('quantity')
#             if not product_id or not quantity:
#                 messages.error(request, "Missing product ID or quantity in the product data.")
#                 return redirect('add_sale')

#             try:
#                 product = Inventory.objects.get(id=product_id)
#             except Inventory.DoesNotExist:
#                 messages.error(request, f"Product with ID {product_id} does not exist.")
#                 return redirect('add_sale')

#             # Check if the stock is sufficient
#             if product.quantity < quantity:
#                 messages.error(request, f"Not enough stock for {product.name}. Available: {product.quantity}.")
#                 return redirect('add_sale')

#         # Create or update Sale
#         if not sale:
#             sale = Sale(customer_name=customer_name, sale_date=sale_date)
#             sale.save()  # Save Sale object
#             print(f"Sale created: {sale.id}")
#             messages.success(request, f"Sale for {customer_name} created successfully.")

#         # Use a transaction to ensure that all database updates happen atomically
#         with transaction.atomic():
#             total_price = 0  # Initialize total price for the sale

#             # Add SaleProduct entries and calculate total price
#             for item in products_data:
#                 product = Inventory.objects.get(id=item['product_id'])
#                 quantity = item['quantity']

#                 # Create SaleProduct entry
#                 sale_product = SaleProduct(
#                     sale=sale,
#                     product=product,
#                     quantity=quantity
#                 )
#                 sale_product.save()  # Save SaleProduct entry
#                 print(f"SaleProduct saved: {sale_product.id}")
#                 total_price += sale_product.total_price  # Add the total price of this product to the sale's total

#                 # Update stock for each product
#                 product.quantity -= quantity  # Subtract the quantity sold
#                 product.save()  # Save the updated product stock
#                 print(f"Product stock updated: {product.id} - New quantity: {product.quantity}")

#             # Update the total price of the sale using the calculate_total_price method
#             sale.calculate_total_price()  # Automatically updates total_price on the sale
#             print(f"Sale updated with total price: {sale.total_price}")

#         # Show a success message and redirect to sale success page with sale details
#         print(f"Redirecting to sale_success with sale_id: {sale.id}")  # Debugging statement
#         messages.success(request, "Sale successfully created!")
#         return redirect('sale_success', sale_id=sale.id)  # Redirect to the success page with sale ID

#     # For GET requests, send products to populate the dropdown
#     inventory_items = Inventory.objects.all()
#     return render(request, 'add_sale.html', {
#         'sale': sale,
#         'inventory_items': inventory_items
#     })

def add_sale(request, pk=None):
    sale = None  # Default to None for new sale

    # Check if pk is provided for editing an existing sale
    if pk:
        sale = get_object_or_404(Sale, pk=pk)

    if request.method == 'POST':
        if not sale:
            # If no sale (edit), create a new Sale object
            sale = Sale.objects.create(
                customer_name=request.POST.get('customer_name'),
                sale_date=request.POST.get('sale_date')
            )

        # Initialize total sale price
        total_sale_price = 0

        # Get the number of products from the hidden field
        num_products = int(request.POST.get('num_products', 1))

        # Create a set of products that are part of this sale (for removal)
        existing_product_ids = set()

        # List to store products with insufficient stock
        out_of_stock_products = []

        for i in range(num_products):
            # Get product id and quantity from the form data
            product_id = request.POST.get(f'product_ids_{i}')
            quantity = request.POST.get(f'quantities_{i}')

            # Skip if product_id or quantity is missing
            if not product_id or not quantity:
                continue

            try:
                # Convert quantity to integer
                quantity = int(quantity)

                # Fetch the product from the inventory
                product = Inventory.objects.get(id=product_id)

                # Check if the requested quantity exceeds the stock available
                if quantity > product.quantity:
                    out_of_stock_products.append(product)
                    continue  # Skip this product

                # Check if stock is 5 or below and show warning
                if product.quantity <= 5:
                    messages.warning(request, f"Warning: Stock for {product.name} is below 5. Available Stock: {product.quantity}.")

                # If we are editing an existing sale, get the original SaleProduct instance
                if pk:
                    sale_product = SaleProduct.objects.filter(sold_to=sale, product=product).first()
                    original_quantity = sale_product.quantity if sale_product else 0
                else:
                    sale_product = None
                    original_quantity = 0

                # If the sale product exists, update the inventory based on quantity change
                if sale_product:
                    if quantity > original_quantity:
                        # Quantity has increased, reduce stock
                        product.quantity -= (quantity - original_quantity)
                    elif quantity < original_quantity:
                        # Quantity has decreased, increase stock
                        product.quantity += (original_quantity - quantity)

                    # Update sale product details
                    sale_product.quantity = quantity
                    sale_product.total_price = product.price * quantity
                    sale_product.save()

                else:
                    # If no SaleProduct exists, create a new one
                    sale_product = SaleProduct.objects.create(
                        sold_to=sale,
                        product=product,
                        quantity=quantity,
                        total_price=product.price * quantity
                    )
                    # Reduce stock if creating a new sale product
                    product.quantity -= quantity

                # Save the updated product quantity in the inventory
                product.save()

                # Add the product's total price to the total sale price
                total_sale_price += sale_product.total_price

                # Add the product id to the existing set (for removal logic later)
                existing_product_ids.add(product_id)

            except ValueError:
                # Handle invalid quantity input
                messages.error(request, f"Invalid quantity for product {i+1}")
                continue
            except Inventory.DoesNotExist:
                # Handle case where product does not exist
                messages.error(request, f"Product {i+1} does not exist in the inventory")
                continue

        # If any products are out of stock, show an error message and stay on the same page
        if out_of_stock_products:
            for product in out_of_stock_products:
                messages.error(request, f"Insufficient stock for product {product.name}. Available: {product.quantity}.")

            # Don't proceed with the sale if any products are out of stock
            return render(request, 'add_sale.html', {
                'products': Inventory.objects.all(),
                'sale': sale,
            })

        # Now handle the case where products were removed from the sale
        if pk:
            # Get all SaleProducts related to this sale and check if they are still in the current selection
            sale_products = SaleProduct.objects.filter(sold_to=sale)

            for sale_product in sale_products:
                if str(sale_product.product.id) not in existing_product_ids:
                    # If the product is no longer selected, remove it from the sale and increase inventory
                    product = sale_product.product
                    product.quantity += sale_product.quantity
                    product.save()

                    # Delete the SaleProduct
                    sale_product.delete()

        # Update total sale price in the Sale object
        sale.total_price = total_sale_price
        sale.save()

        # Success message and redirect
        messages.success(request, f"Sale #{sale.id} {'updated' if pk else 'added'} successfully!")
        return redirect('sale_list')  # Redirect to the sales list page or any other page

    # Handle GET requests and search functionality
    search_query = request.GET.get('search', '')
    products = Inventory.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    return render(request, 'add_sale.html', {
        'products': products,
        'sale': sale,
    })



def sale_list(request):
    sales = Sale.objects.all().prefetch_related('sale_products__product')
    
    # Calculate total sale price for each sale
    for sale in sales:
        sale.calculate_total_price()

    return render(request, 'sale_list.html', {'sales': sales})


def print_sale(request, sale_id):
    # Retrieve the specific sale using the sale_id
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Get the customer associated with the sale
    customer = sale.customer_name  # Assuming 'customer_name' is the field representing the customer

    # Retrieve all sales made by this customer
    customer_sales = Sale.objects.filter(customer_name=customer)

    # Collect all SaleProducts from these sales
    all_sale_products = SaleProduct.objects.filter(sold_to__in=customer_sales)

    # Calculate the total price for this sale
    total_price = sum(sale_product.total_price for sale_product in all_sale_products)

    # Render the page with sale, sale products, and total price
    return render(request, 'print_sale.html', {
        'sale': sale,
        'sale_products': sale.sale_products.all(),
        'all_sale_products': all_sale_products,
        'total_price': total_price,  # Add total_price to context
    })


def edit_sale(request, id):
    sale = get_object_or_404(Sale, id=id)
    
    if request.method == 'POST':
        # Handle form submission to edit sale details
        pass
    
    return render(request, 'edit_sale.html', {'sale': sale})

# def delete_sale(request, id):
#     sale = get_object_or_404(Sale, id=id)
#     sale.delete()
#     return redirect('sale_list')  # Redirect to the sales list after deletion


def confirm_sale(request, sale_id):
    # Use get_object_or_404 to fetch the Sale by its ID. If it doesn't exist, it will return a 404 error.
    sale = get_object_or_404(Sale, id=sale_id)

    # Check if the sale is already confirmed
    if not sale.is_confirmed:
        # Use a transaction to ensure both the sale and its products are confirmed together
        with transaction.atomic():
            # Set is_confirmed to True for the sale
            sale.is_confirmed = True
            sale.save()

            # Update is_confirmed for each SaleProduct in this sale (if needed)
            for sale_product in sale.sale_products.all():
                if not sale_product.is_confirmed:
                    sale_product.is_confirmed = True
                    sale_product.save()
    
    # Redirect to the sales list page after confirmation
    return redirect('sale_list')  # Ensure this matches the correct URL name for the sales list page
 # Ensure this matches the correct URL name for the sales list page


def remove_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Delete the sale
    sale.delete()

    # Redirect back to the sale list with a success message
    messages.success(request, f"Sale #{sale.id} has been removed.")
    return redirect('sale_list')



# def sale_success(request, sale_id):
#     # Retrieve the sale using the sale_id
#     try:
#         sale = Sale.objects.get(id=sale_id)
#     except Sale.DoesNotExist:
#         messages.error(request, "Sale not found.")
#         return redirect('add_sale')

#     # Prepare the sale data to display on the success page
#     sale_products = []
#     for item in sale.products:
#         product = Inventory.objects.get(id=item['product_id'])
#         quantity = item['quantity']
#         price = product.price
#         total_price = price * quantity
#         sale_products.append({
#             'product_name': product.name,
#             'quantity': quantity,
#             'price': price,
#             'total_price': total_price
#         })

#     total_price = sale.total_price

#     return render(request, 'sale_success.html', {
#         'customer_name': sale.customer_name,
#         'sale_date': sale.sale_date,
#         'sale_products': sale_products,
#         'total_price': total_price
#     })


# def sale_success(request, sale_id):
#     try:
#         sale = Sale.objects.get(id=sale_id)
#     except Sale.DoesNotExist:
#         messages.error(request, "Sale not found.")
#         return redirect('add_sale')

#     # Render the success page with the sale details
#     return render(request, 'sale_success.html', {
#         'sale': sale
#     })


def view_sales(request):
    
    return render(request, 'supplier_list.html')



# def sale_list(request):
#     # You can filter sales by date or other fields if needed
#     sales = Sale.objects.filter(sale_date__gte=datetime(2024, 1, 1))  # Example: Filter by date

#     sale_details = []
    
   

#     return render(request, 'sale_list.html', {'sale_details': sale_details})


# forgot password view

def forgot_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "User with this email doesn't exist"}, status=400)

        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.id).encode())

        # Get current domain (useful for sending the URL in the email)
        current_site = get_current_site(request)
        reset_link = f"http://{current_site.domain}/reset-password/{uid}/{token}"

        # Send email with the password reset link
        subject = "Password Reset Request"
        message = render_to_string(
            "accounts/password_reset_email.html",  # Create a template for the email
            {"reset_link": reset_link, "user": user}
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        return JsonResponse({"message": "Password reset link sent to your email."}, status=200)
    
    return JsonResponse({"error": "Invalid request method."}, status=400)



# accounts/views.py
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth import get_user_model
# from django.http import JsonResponse
# from django.contrib.auth.forms import PasswordChangeForm

def reset_password(request, uidb64, token):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_password = data.get('new_password')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(id=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            return JsonResponse({"error": "Invalid user or token"}, status=400)

        # Check if the token is valid
        if not default_token_generator.check_token(user, token):
            return JsonResponse({"error": "Invalid or expired token"}, status=400)

        # Set the new password
        user.set_password(new_password)
        user.save()

        return JsonResponse({"message": "Password successfully reset."}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=400)




from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'  # Your custom template for the form
    email_template_name = 'registration/password_reset_email.html'  # Customize the email
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')  # Redirect after password reset request

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'  # Your custom template for reset confirmation
    success_url = reverse_lazy('password_reset_complete')  # Redirect after successful password reset




