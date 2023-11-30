import django_filters
from django_filters import rest_framework as filters

from inventory.models import Brand, Category, ProductInventory
from inventory.utils import CONDITION_CHOICES


class ProductInventoryFilter(django_filters.FilterSet):
    brand = filters.ModelChoiceFilter(queryset=Brand.objects.all(), field_name='brand__name', to_field_name='name')
    color = filters.CharFilter(field_name='color__name')
    storage = filters.CharFilter(field_name='storage_size__size', lookup_expr='icontains')
    attribute_name = filters.CharFilter(field_name="attribute_values__product_attribute__name", lookup_expr='icontains')
    attribute_value = filters.CharFilter(field_name="attribute_values__attribute_value", lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name="store_price", lookup_expr='gte', help_text="Filter by minimum price.")
    price_max = django_filters.NumberFilter(field_name="store_price", lookup_expr='lte', help_text="Filter by maximum price.")
    condition = django_filters.ChoiceFilter(choices=CONDITION_CHOICES, help_text="Filter by condition.")
    
    class Meta:
        model = ProductInventory
        fields = [
            'product__name', 
            'brand', 
            'color', 
            'storage', 
            'attribute_name', 
            'attribute_value', 
            'price_min', 
            'price_max', 
            'condition'
        ]


# http://127.0.0.1:8000/api/inventory/products/?storage=256GB 4GB RAM
# http://127.0.0.1:8000/api/inventory/products/?color=Silver
# http://127.0.0.1:8000/api/inventory/products/?brand=Apple
# http://127.0.0.1:8000/api/inventory/products/?attribute_name=Display Size
# http://127.0.0.1:8000/api/inventory/products/?attribute_value=6.1 inches
# http://127.0.0.1:8000/api/inventory/products/?price_min=50
# http://127.0.0.1:8000/api/inventory/products/?condition=used
# # Get all products with a sale_price >= 50
# http://127.0.0.1:8000/api/inventory/products/?price_min=50

# # Get all products with a sale_price <= 100
# http://127.0.0.1:8000/api/inventory/products/?price_max=100

# # Get all products with a sale_price between 50 and 100
# http://127.0.0.1:8000/api/inventory/products/?price_min=50&price_max=100


# class ProductInventoryFilter(django_filters.FilterSet):
#     brand_name = django_filters.CharFilter(field_name="brand__name", lookup_expr='iexact')
#     color_name = django_filters.CharFilter(field_name="color__name", lookup_expr='iexact')
#     color_hex = django_filters.CharFilter(field_name="color__hex_code", lookup_expr='iexact')
#     storage_size = django_filters.CharFilter(field_name="storage__size", lookup_expr='iexact')

#     class Meta:
#         model = ProductInventory
#         fields = [
#             'product__name', 
#             'brand_name',
#             'color_name',
#             'color_hex'
#         ]
