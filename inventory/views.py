import re

from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views.generic import TemplateView, View
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory import forms, utils
from inventory.filters import ProductInventoryFilter
from inventory.models import (Brand, Category, Color, Media, Product,
                              ProductAttribute, ProductAttributeValue,
                              ProductInventory, ProductType, Stock, Storage)
from inventory.populate import delete_data, populate_data
from inventory.serializers import (AllProductInventorySerializer,
                                   BrandSerializer, CategorySerializer,
                                   ProductInventoryDetailSerializer,
                                   ProductInventorySerializer,
                                   ProductSuggestionSerializer,
                                   TrendingCategorySerializer)


# ------------------------- CUSTOM UTILITY -------------------------
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
# ------------------------- CUSTOM UTILITY -------------------------


# ------------------------- HOME PAGE -------------------------
class TrendingCategoriesView(APIView):
    @swagger_auto_schema(operation_description="Retrieve the list of trending categories. This data is cached for 1 hour for performance optimization.")
    def get(self, request):
        data = cache.get('trending_categories')

        if not data:
            trending = Category.objects.filter(is_trending=True)
            serializer = TrendingCategorySerializer(trending, many=True)
            data = serializer.data
            cache.set('trending_categories', data, 3600)  # Cache for 1 hour
        return Response(data)


class OnSaleProductInventoryView(generics.ListAPIView):
    queryset = ProductInventory.objects.exclude(sale_price=None)
    serializer_class = ProductInventorySerializer

    @swagger_auto_schema(operation_description="Retrieve a list of product inventories that are currently on sale.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
# ------------------------- HOME PAGE -------------------------


# ------------------------- PRODUCTS PAGES -------------------------
class AllProductListView(generics.ListAPIView):
    queryset = ProductInventory.objects.all().order_by('created_at')
    serializer_class = AllProductInventorySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['product__name', 'sku']
    filterset_class = ProductInventoryFilter
    pagination_class = StandardResultsSetPagination # PageNumberPagination

    @swagger_auto_schema(operation_description="Retrieve a list of all product inventories available in the database. You can filter and search through these inventories using the provided query parameters.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        # Use the parent class's implementation to get initial filtering
        queryset = super().filter_queryset(queryset)
        
        # Get category parameter from query parameters
        category_param = self.request.query_params.get('category', None)
        
        if category_param:
            try:
                # Find the category object
                category = Category.objects.get(name=category_param)

                # Fetch all descendants of that category
                descendant_categories = category.get_descendants(include_self=True)
                
                # Update the queryset to include products belonging to any of the fetched categories
                queryset = queryset.filter(product__category__in=descendant_categories)
            except Category.DoesNotExist:
                # Handle case where category does not exist, if needed
                pass
        
        return queryset


class ProductSuggestionView(generics.ListAPIView):
    queryset = ProductInventory.objects.all()
    serializer_class = ProductSuggestionSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', None)

        if query:
            # Look for matching product names or SKUs. Adjust this if needed.
            return ProductInventory.objects.filter(
                Q(product__name__icontains=query) | Q(sku__icontains=query)
            ).values('product__name').distinct().order_by('product__name')
        return ProductInventory.objects.none()

    
class ProductDetailView(generics.RetrieveAPIView):
    queryset = ProductInventory.objects.all()
    serializer_class = ProductInventoryDetailSerializer
    lookup_field = 'sku'  # Assuming you want to use the SKU as the lookup field.

    @swagger_auto_schema(operation_description="Retrieve details of a single product inventory based on its SKU. Provide SKU in the path to get detailed information about the product, including price, storage size, color, and other attributes.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Define the Prefetch object for attribute_values
        attribute_values_prefetch = Prefetch(
            'attribute_values',
            queryset=ProductAttributeValue.objects.select_related('product_attribute')
        )
        
        queryset = ProductInventory.objects.select_related(
            'color', 'storage_size', 'product_type', 'product', 'brand'
        ).prefetch_related(
            attribute_values_prefetch  # Adding the prefetch here
        ).all()
        
        color = self.request.query_params.get('color', None)
        storage_size = self.request.query_params.get('storage_size', None)
        
        if color:
            queryset = queryset.filter(color__name=color)
        if storage_size:
            queryset = queryset.filter(storage_size__size=storage_size)
        
        return queryset
# ------------------------- PRODUCTS PAGE -------------------------


# -------------------- FILTER VIEWS -----------------------
class CategoryTreeView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request):
        queryset = self.get_queryset().filter(level=0, is_active=True) 
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
# -------------------- EXTRAS -----------------------


# -------------------- UPDATE -----------------------
def remove_special_characters(string):
    return re.sub(r"[^\w\s]", "", string)


class UpdateView(View):
    template_name = "update/updateform.html"

    def get(self, request, *args, **kwargs):
        form = forms.ProductInventoryForm()
        context = {"form": form}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.ProductInventoryForm(request.POST or None, request.FILES)
        
        if form.is_valid():
            # category
            category_name = form.cleaned_data.get("category_name")
            category_slug = remove_special_characters(category_name).replace(" ", "-")         
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': category_slug,
                }
            )
            
            # product
            product_name = form.cleaned_data.get("product_name")
            product_description = form.cleaned_data.get("product_description")
            product_slug = remove_special_characters(product_name).replace(" ", "-")
            
            if Product.objects.last():
                latest_product = Product.objects.last()
                latest_product_web_id = latest_product.web_id
            else: 
                latest_product_web_id = 00000000
            product_web_id = f"{int(latest_product_web_id) + 1}"
            new_product = Product(
                web_id=product_web_id,
                slug=product_slug,
                name=product_name,
                description=product_description,
            )
            new_product.save()
            new_product.category.set([category])

            # product type
            product_type_name = form.cleaned_data.get("product_type_name")
            product_type, product_type_created = ProductType.objects.get_or_create(
                name=product_type_name
            )
            if product_type_created:
                product_type.save()

            # Brand
            brand_name = form.cleaned_data.get("brand_name")
            product_brand, product_brand_created = Brand.objects.get_or_create(name=brand_name)
            if product_brand_created:
                product_brand.save()

            # Color
            color_name = form.cleaned_data.get("color_name")
            hex_code = utils.COLOR_CHOICES[color_name]
            product_color, product_color_created = Color.objects.get_or_create(
                name=color_name, hex_code=hex_code
            )
            if product_color_created:
                product_color.save()

            # Storage
            storage_size = form.cleaned_data.get("storage_size")
            product_storage_size, product_storage_size_created = Storage.objects.get_or_create(
                size=storage_size
            )
            if product_storage_size_created:
                product_storage_size.save()

            # Product Inventory
            product_default = form.cleaned_data.get("product_default")
            product_retail_price = form.cleaned_data.get("product_retail_price")
            product_store_price = form.cleaned_data.get("product_store_price")
            product_discount_store_price = form.cleaned_data.get("product_discount_store_price")
            product_sale_price = form.cleaned_data.get("product_sale_price")
            weight = form.cleaned_data.get("weight")
            stock_units = form.cleaned_data.get("stock_units")
            
            if ProductInventory.objects.last():
                latest_inventory = ProductInventory.objects.last()
                latest_inventory_sku = int(latest_inventory.sku)
                latest_inventory_upc = int(latest_inventory.upc)
            else:
                latest_inventory_sku = 000000
                latest_inventory_upc = 000000
            SKU = f"{latest_inventory_sku + 1}"
            UPC = f"{latest_inventory_upc + 1}"
            new_inventory = ProductInventory(
                sku=SKU,
                upc=UPC,
                is_default=product_default,
                retail_price=product_retail_price,
                store_price=product_store_price,
                discount_store_price=product_discount_store_price,
                sale_price=product_sale_price,
                weight=weight,
                product_type=product_type,
                product=new_product,
                brand=product_brand,
                color=product_color,
                storage_size=product_storage_size,
            )

            new_inventory.save()

            # Product Attribute
            attributes = {
                "wireless_carrier": "Wireless Carrier",
                "operating_system": "Operating System",
                "cellular_technology": "Cellular Technology",
                "memory_storage_capacity": "Memory Storage Capacity",
                "connectivity_technology": "Connectivity Technology",
                "screen_size": "Screen Size",
            }

            for product_type_attribute_name_frontend, product_type_attribute_name in attributes.items():
                product_type_attribute_value = form.cleaned_data.get(product_type_attribute_name_frontend)

                if product_type_attribute_value:
                    try:
                        product_type_attribute_description = utils.ATTRIBUTE_CHOICES[product_type_attribute_name_frontend]
                    except:
                        product_type_attribute_description = "There is no description for this attribute"
                    (
                        product_type_attribute,
                        product_type_attribute_created,
                    ) = ProductAttribute.objects.get_or_create(
                        name=product_type_attribute_name, description=product_type_attribute_description
                    )
                    if product_type_attribute_created:
                        product_type_attribute.save()
                    product_type.product_type_attributes.add(product_type_attribute)

                    product_attribute_value = ProductAttributeValue(
                        product_attribute=product_type_attribute, attribute_value=product_type_attribute_value
                    )
                    # product_attribute_value.product_attribute = product_type_attribute
                    product_attribute_value.save()

                    new_inventory.attribute_values.add(product_attribute_value)
                    new_inventory.save()

            # Product Stock
            product_stock = Stock(product_inventory=new_inventory, units=stock_units)
            product_stock.save()

            # Product Media
            image_1 = form.cleaned_data.get("image_1")
            image_2 = form.cleaned_data.get("image_2")
            image_3 = form.cleaned_data.get("image_3")
            image_4 = form.cleaned_data.get("image_4")
            image_name = form.cleaned_data.get("image_name")

            if image_1:
                Media.objects.create(
                    product_inventory=new_inventory, image=image_1, alt_text=image_name, is_feature=True
                )
            if image_2:
                Media.objects.create(
                    product_inventory=new_inventory, image=image_2, alt_text=image_name, is_feature=False
                )
            if image_3:
                Media.objects.create(
                    product_inventory=new_inventory, image=image_3, alt_text=image_name, is_feature=False
                )
            if image_4:
                Media.objects.create(
                    product_inventory=new_inventory, image=image_4, alt_text=image_name, is_feature=False
                )
        else:
            print("form not valid")
        return redirect("update_done")


class UpdateDoneView(TemplateView):
    template_name = "update/update_done.html"


def add_product(request):
    if request.method == 'POST':
        form = forms.ProductForm(request.POST, request.FILES)
        if form.is_valid():
            last_product = Product.objects.order_by('web_id').last()
            new_web_id = '00001'  # Default starting web_id

            if last_product and last_product.web_id:
                new_web_id = str(int(last_product.web_id) + 1).zfill(5)  # Auto-increment web_id

            product = form.save(commit=False)
            product.web_id = new_web_id
            product.slug = slugify(product.name)  # Generate slug from the new product's name
            product.save()
            
            return redirect("update_done")  # Ensure this URL is defined in your urls.py
    else:
        form = forms.ProductForm()

    return render(request, 'update/creation.html', {'form': form})


def add_category(request):
    if request.method == 'POST':
        form = forms.CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("update_done")  # Make sure this URL name exists in your URL patterns
    else:
        form = forms.CategoryForm()

    return render(request, 'update/creation.html', {'form': form})


def generate_unique_identifiers():
    last_inventory = ProductInventory.objects.order_by('sku').last()
    if last_inventory:
        last_number = int(last_inventory.sku.split('-')[-1])
        new_number = str(last_number + 1).zfill(7)
    else:
        new_number = '0000001'

    return f'SKU-{new_number}', f'UPC-{new_number}'


def add_product_inventory(request):
    if request.method == 'POST':
        form = forms.ProductInventoryForm(request.POST, request.FILES)
        if form.is_valid():
            product_inventory = form.save(commit=False)
            storage_sizes = form.cleaned_data['storage_sizes']
            colors = form.cleaned_data['colors']

            for storage_size in storage_sizes:
                for color in colors:
                    # Generate unique SKU and UPC
                    new_sku, new_upc = generate_unique_identifiers()
                    ProductInventory.objects.create(
                        product=product_inventory.product,
                        brand=product_inventory.brand,
                        storage_size=storage_size,
                        color=color,
                        sku=new_sku,
                        upc=new_upc,
                        # Include other fields as needed
                    )
            return redirect('update_done')
    else:
        form = forms.ProductInventoryForm()

    return render(request, 'update/creation.html', {'form': form})


def add_product_attribute_value(request):
    if request.method == 'POST':
        form = forms.ProductAttributeValueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('update_done')
    else:
        form = forms.ProductAttributeValueForm()

    return render(request, 'update/creation.html', {'form': form})
# -------------------- UPDATE -----------------------


# -------------------- TEST -----------------------
class Test(APIView):
    def get(self, request):
        
        populate_data()
        # delete_data()

        return JsonResponse({"done": "done"})