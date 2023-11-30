from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import OuterRef, Subquery

from inventory import models


class TopmostProductTypeFilter(SimpleListFilter):
    title = 'Topmost Product Type'  # Human-readable title for the filter
    parameter_name = 'topmost'  # Parameter that'll be used in the query string

    def lookups(self, request, model_admin):
        topmost_product_types = models.ProductType.objects.filter(parent__isnull=True)
        return [(pt.id, pt.name) for pt in topmost_product_types]

    def queryset(self, request, queryset):
        if self.value():
            # Convert the value to integer
            topmost_product_type_id = int(self.value())
            
            # If your hierarchy is deep, you might want to optimize this further.
            descendants = models.ProductType.objects.get(id=topmost_product_type_id).get_descendants(include_self=True)
            return queryset.filter(id__in=descendants)
        return queryset
    

def duplicate_product_inventory(modeladmin, request, queryset):
    for existing_inventory in queryset:
        # Create a new instance of the ProductInventory model
        new_inventory = models.ProductInventory()
        
        # Generate new SKU and UPC values
        sku = existing_inventory.sku
        upc = existing_inventory.upc

        new_sku = "sku-000" + str(int(sku.split('-')[1]) + 1)
        new_upc = "upc-000" + str(int(upc.split('-')[1]) + 1)
        
        # Assign the field values from the existing inventory to the new inventory
        new_inventory.sku = new_sku
        new_inventory.upc = new_upc
        new_inventory.name = existing_inventory.name
        new_inventory.product_type = existing_inventory.product_type
        new_inventory.product = existing_inventory.product
        new_inventory.brand = existing_inventory.brand
        new_inventory.color = existing_inventory.color
        new_inventory.storage_size = existing_inventory.storage_size
        new_inventory.is_active = existing_inventory.is_active
        new_inventory.is_default = existing_inventory.is_default
        new_inventory.retail_price = existing_inventory.retail_price
        new_inventory.store_price = existing_inventory.store_price
        new_inventory.discount_store_price = existing_inventory.discount_store_price
        new_inventory.sale_price = existing_inventory.sale_price
        new_inventory.weight = existing_inventory.weight
        new_inventory.condition = existing_inventory.condition

        # Save the duplicated instance
        new_inventory.save()

        # Duplicate the associated media (images)
        for media in existing_inventory.media_product_inventory.all():
            new_media = models.Media()
            new_media.product_inventory = new_inventory
            new_media.image = media.image
            new_media.alt_text = media.alt_text
            new_media.is_feature = media.is_feature
            new_media.save()

    # Provide a feedback message for the admin interface
    message = "Selected product inventory items have been duplicated."
    modeladmin.message_user(request, message)    

duplicate_product_inventory.short_description = "Duplicate selected product inventory"


class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'domain')


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["id", "name", "slug", "is_active", "is_trending"]
    search_fields = ['name', "is_active", "is_trending"]


class Color(admin.ModelAdmin):
    list_display = ['name', 'hex_code']
    search_fields = ['name', ]


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ['name', ]


class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_topmost_parent')  # , 'get_product_attributes')
    search_fields = ['name', ]
    list_filter = (TopmostProductTypeFilter, )

    # def get_product_attributes(self, obj):
    #     return ", ".join([str(attribute) for attribute in obj.product_type_attributes.all()])

    def get_topmost_parent(self, obj):
        return self.topmost_parents.get(obj.topmost_parent_id) if obj.topmost_parent_id else None

    def get_queryset(self, request):
        # Annotate each ProductType with the ID of its topmost parent.
        qs = super().get_queryset(request)
        
        # Subquery to find the topmost parent's ID
        topmost_parent_id = models.ProductType.objects.filter(
            id=OuterRef('parent_id') 
        ).values('id')[:1]

        qs = qs.annotate(
            topmost_parent_id=Subquery(topmost_parent_id)
        )

        # Cache the names of the topmost parents for use in get_topmost_parent
        self.topmost_parents = {
            product_type.id: product_type.name
            for product_type in models.ProductType.objects.filter(id__in=qs.values_list('topmost_parent_id', flat=True))
        }

        return qs

    get_topmost_parent.short_description = 'Topmost Parent'


class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['product_attribute', 'attribute_value', 'display_associated_products']
    search_fields = ['product_attribute', ]

    def display_associated_products(self, obj):
        return ", ".join([str(product) for product in obj.products.all()])
    display_associated_products.short_description = 'Associated Products'


class ProductAttributeValuesAdmin(admin.ModelAdmin):
    list_display = ['attributevalues', 'productinventory']


class ProductTypeAttributeAdmin(admin.ModelAdmin):
    list_display = ['product_type', 'product_attribute']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['web_id', 'name', 'slug', 'is_active', 'created_at', 'updated_at']
    prepopulated_fields = {"slug": ("name",)}
    

class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = [
        'sku', 'upc', 'get_product_name', 'get_product_inventory_color', 
        'get_product_inventory_storage', 'condition']
    search_fields = ['product_attribute', ]
    list_filter = [
        'product__name', 'color__name', 'storage_size__size', 'condition'
    ]

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_inventory_color(self, obj):
        return obj.color.name
    
    def get_product_inventory_storage(self, obj):
        if obj.storage_size:
            return obj.storage_size.size
        else:
            return None 
    
    get_product_name.short_description = 'Product Name'
    get_product_inventory_color.short_description = 'Product Color'
    get_product_inventory_storage.short_description = 'Product Storage'

    actions = [duplicate_product_inventory]


class MediaAdmin(admin.ModelAdmin):
    list_display = ['get_product_inventory_sku', 'get_product_description', 'alt_text', 'is_feature']
    search_fields = ['alt_text', 'product_inventory__sku', 'product_inventory__product__name', 'product_inventory__color__name']
    
    def get_product_inventory_sku(self, obj):
        return obj.product_inventory.sku

    def get_product_description(self, obj):
        if obj.product_inventory.storage_size:
            return f"{obj.product_inventory.product.name} - {obj.product_inventory.color.name} - {obj.product_inventory.storage_size.size}"
        else:
            return f"{obj.product_inventory.product.name} - {obj.product_inventory.color.name}"

    get_product_inventory_sku.short_description = 'Product SKU'
    get_product_description.short_description = 'Product Description'


admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Brand)
admin.site.register(models.Color)
admin.site.register(models.Storage)
admin.site.register(models.ProductAttribute, ProductAttributeAdmin)
admin.site.register(models.ProductType, ProductTypeAdmin)
admin.site.register(models.ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(models.ProductInventory, ProductInventoryAdmin)
admin.site.register(models.Media, MediaAdmin)
admin.site.register(models.Stock)
admin.site.register(models.ProductAttributeValues, ProductAttributeValuesAdmin)
admin.site.register(models.ProductTypeAttribute, ProductTypeAttributeAdmin)
