from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('accounts/login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.index, name='home'),
    path('add/', views.add_inventory, name='add_inventory'),
    path('aditin/', views.add_inventory, name='add_inventory'),
    path('edit/<int:pk>/', views.add_inventory, name='add_inventory'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('Delete Inventory/<int:pk>/<str:object_type>/', views.delete, name='delete_inventory'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('supplier/add/', views.add_supplier, name='add_supplier'),  # Add new supplier
    path('supplier/edit/<int:pk>/', views.add_supplier, name='edit_supplier'),  # Edit existing supplier
    path('supplier/list/', views.supplier_list, name='supplier_list'), 
   
    path('search_inventory/', views.search_inventory, name='search_inventory'),
    path('Add Sale/', views.add_sale, name='add_sale'), 
      # path('sale-success/<int:sale_id>/', views.sale_success, name='sale_success'),

    #sale url
   
    path('View Sale/', views.sale_list, name='sale_list'), 
    #      path('update-stock/', views.update_stock, name='update_stock'),
    #     #   path('sale-success/<int:sale_id>/', views.sale_success, name='sale_success'),
    path('sales/', views.sale_list, name='sale_list'),
          path('sale/edit/<int:pk>/', views.add_sale, name='edit_sale'),
    path('sale/delete/<int:pk>/<str:object_type>/', views.delete, name='delete_sale'),
    path('sale/print/<int:sale_id>/', views.print_sale, name='print_sale'),
        #  path('sale/print/<int:sale_id>/', views.print_sale, name='print_sale'),
    path('sales/confirm/<int:sale_id>/', views.confirm_sale, name='confirm_sale'),
    path('sales/remove/<int:sale_id>/', views.remove_sale, name='remove_sale'),
    path('suppliers/delete/<int:pk>/<str:object_type>/', views.delete, name='delete_supplier'),

    
]

