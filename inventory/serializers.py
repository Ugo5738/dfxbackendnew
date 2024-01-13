from rest_framework import serializers

from inventory.models import (Brand, Category, Media, Product,
                              ProductAttributeValue, ProductInventory, Stock)


# ----------------------- HOME PAGE -----------------------
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['image', 'alt_text', 'is_feature']


class SampleProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'image']

    def get_image(self, obj):
        # Get the first product inventory for the product
        inventory = obj.product.first()

        # If there's an inventory, get the first media image
        if inventory:
            media = inventory.media_product_inventory.filter(is_feature=True).first()
            # If no featured media found, get any associated media
            if not media:
                media = inventory.media_product_inventory.first()
            if media:
                return media.image.url
        return None


class TrendingCategorySerializer(serializers.ModelSerializer):
    sample_product = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'sample_product']

    def get_sample_product(self, obj):
        # Start with the object itself
        categories_to_check = [obj]
        
        # Add the children of the object to the list
        categories_to_check.extend(list(obj.get_descendants()))

        # Loop through categories, including children, and find the first product
        for category in categories_to_check:
            sample_product = category.product_set.first()
            if sample_product:
                # Serialize the found product
                return SampleProductSerializer(sample_product).data

        # Return None if no sample product found in category or any child categories
        return None
    

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active', 'is_trending', 'children')

    def get_children(self, obj):
        if obj.is_active:  # or any other condition you want to apply
            serializer = CategorySerializer(obj.children.filter(is_active=True), many=True, context=self.context)
            return serializer.data
        return []


# class CategorySerializer(serializers.ModelSerializer):
#     products = ProductSerializer(many=True, read_only=True)
#     # first_product_image = serializers.SerializerMethodField()
#     children = RecursiveField(many=True)

#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'is_trending', 'first_product_image', 'products', 'children']

#     # def get_first_product_image(self, obj):
#     #     # Checks products in the current category
#     #     if obj.products and obj.products[0].media_product_inventory:
#     #         return obj.products[0].media_product_inventory[0].image.url

#     #     # Checks products in the child categories
#     #     for child in obj.children.all():
#     #         image = self.get_first_product_image(child)
#     #         if image:
#     #             return image

#     #     return None
    

class ProductInventorySerializer(serializers.ModelSerializer):
    default_image = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductInventory
        fields = ['sku', 'product_name', 'store_price', 'sale_price', 'default_image', 'condition'] 

    def get_default_image(self, obj):
        # Get the default media image for the product inventory
        media = obj.media_product_inventory.filter(is_feature=True).first()

        # If there's a default media image, return its URL, else return None
        return media.image.url if media else None

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return None
# ------------------------- HOME PAGE -------------------------

# ----------------------- PRODUCTS PAGE -----------------------
class AllProductInventorySerializer(serializers.ModelSerializer):
    default_image = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductInventory
        fields = ['sku', 'product_name', 'store_price', 'discount_store_price', 'default_image', 'condition'] 

    def get_default_image(self, obj):
        # Get the default media image for the product inventory
        media = obj.media_product_inventory.filter(is_feature=True).first()

        # If there's a default media image, return its URL, else return None
        return media.image.url if media else None

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return None
# ----------------------- PRODUCTS PAGE -----------------------


# ----------------------- PRODUCTS DETAIL PAGE -----------------------
class ProductSerializer(serializers.ModelSerializer):
    formatted_description = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('web_id', 'slug', 'name', 'description', 'formatted_description', 'category', 'is_active')

    def get_formatted_description(self, obj):
        # Assuming each point starts with a '-' followed by a space
        return [point.strip() for point in obj.description.split('-') if point.strip()]


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('last_checked', 'units', 'units_sold')


class ProductInventoryDetailSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name')
    color_name = serializers.CharField(source='color.name')
    storage_size = serializers.CharField(source='storage_size.size', required=False)
    attribute_values = serializers.SerializerMethodField()
    product_details = ProductSerializer(source='product')
    images = serializers.SerializerMethodField()
    banner_image = serializers.SerializerMethodField()

    variants = serializers.SerializerMethodField()

    # attribute_values = serializers.StringRelatedField(many=True)
    # images = MediaSerializer(source='media_product_inventory', many=True)

    class Meta:
        model = ProductInventory
        fields = (
            'sku', 'upc', 'name', 'seo_feature', 'product_type', 'product_details', 
            'brand_name', 'color_name', 'storage_size', 'attribute_values', 'is_active', 
            'is_default', 'store_price','discount_store_price', 'sale_price', 'condition',
            'weight', 'created_at', 'updated_at', 'variants', 'images', 'shipping', 
            'onsite_pickup', 'banner_image',
        )
    
    def get_attribute_values(self, obj):
        attribute_values = ProductAttributeValue.objects.filter(
            attributevaluess__productinventory=obj
        ).select_related('product_attribute')
        return attribute_values_to_dict(attribute_values)
    
    def get_images(self, obj):
        # Filter out banner images
        media_objects = obj.media_product_inventory.filter(banner=False)
        return MediaSerializer(media_objects, many=True).data
    
    def get_banner_image(self, obj):
        media = obj.media_product_inventory.filter(banner=True).first()  # Assumes only one banner per product
        if media:
            return media.image.url 
        return None  
    
    def get_variants(self, obj):
        same_type_products = ProductInventory.objects.filter(
            product_type=obj.product_type,
            product=obj.product
        ).select_related('color', 'storage_size')
        
        variant_data = {}
        for product in same_type_products:
            if product.product.id == obj.product.id:
                variant_data.setdefault(
                    product.color.name,
                    {'hex_code': product.color.hex_code, 'available_storage': {}}
                )['available_storage'].setdefault(
                    product.storage_size.size if product.storage_size else None,
                    product.sku
                )
            
        return variant_data
# ----------------------- PRODUCTS DETAIL PAGE -----------------------


# ----------------------- HELPER FUNCTIONS -----------------------
def attribute_values_to_dict(attribute_values):
    return {
        attribute_value.product_attribute.name: attribute_value.attribute_value
        for attribute_value in attribute_values
    }
# ----------------------- HELPER FUNCTIONS -----------------------


# ----------------------- FILTERS -----------------------
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']


# ----------------------- SEARCH -----------------------
class ProductSuggestionSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductInventory
        fields = ('product_name',)

    def get_product_name(self, obj):
        product_name = obj.get('product__name', '') if isinstance(obj, dict) else obj.product.name
        return product_name
