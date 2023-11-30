from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.http.response import JsonResponse
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.filters import ProductInventoryFilter
from inventory.models import (Brand, Category, ProductAttributeValue,
                              ProductInventory)
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


# -------------------- TEST -----------------------
class Test(APIView):
    def get(self, request):
        
        populate_data()
        # delete_data()

        return JsonResponse({"done": "done"})