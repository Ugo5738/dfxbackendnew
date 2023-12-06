import secrets

from django.db import models
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField

from inventory.utils import CONDITION_CHOICES


class Category(MPTTModel):
    """
    Inventory Category table implimented with MPTT
    """

    name = models.CharField(
        max_length=100,
        null=False,
        unique=False,
        blank=False,
        verbose_name=_("category name"),
        help_text=_("format: required, max-100"),
    )
    slug = models.SlugField(
        max_length=150,
        null=False,
        unique=False,
        blank=False,
        verbose_name=_("category safe URL"),
        help_text=_("format: required, letters, numbers, underscore, or hyphens"),
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_trending = models.BooleanField(
        db_index=True,
        default=False,
        verbose_name=_("is trending"),
        help_text=_("Check this field if the category is trending."),
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        # on_delete=models.SET_NULL,
        related_name="children",
        null=True,
        blank=True,
        unique=False,
        verbose_name=_("parent of category"),
        help_text=_("format: not required"),
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("product category")
        verbose_name_plural = _("product categories")

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        # Before deleting the category, re-link children to their grandparent
        if self.parent:
            self.children.all().update(parent=self.parent)
        super(Category, self).delete(*args, **kwargs)


class Product(models.Model):
    """
    Product details table
    """

    web_id = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("product website ID"),
        help_text=_("format: required, unique"),
    )
    slug = models.SlugField(
        max_length=255,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("product safe URL"),
        help_text=_("format: required, letters, numbers, underscores or hyphens"),
    )
    name = models.CharField(
        max_length=255,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("product name"),
        help_text=_("format: required, max-255"),
    )
    description = models.TextField(
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("product description"),
        help_text=_("format: required"),
    )
    category = TreeManyToManyField(Category)
    
    is_active = models.BooleanField(
        unique=False,
        null=False,
        blank=False,
        default=True,
        verbose_name=_("product visibility"),
        help_text=_("format: true=product visible"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("date product created"),
        help_text=_("format: Y-m-d H:M:S"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("date product last updated"),
        help_text=_("format: Y-m-d H:M:S"),
    )

    def __str__(self):
        return self.name


class Brand(models.Model):
    """
    Product brand table
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("brand name"),
        help_text=_("format: required, unique, max-255"),
    )

    def __str__(self):
        return self.name


class Color(models.Model):
    """
    Product color table
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("color name"),
        help_text=_("format: required, unique, max-255"),
    )

    hex_code = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("HEX code"),
        help_text=_("format: required, unique, max-255"),
    )

    def __str__(self):
        return self.name


class Storage(models.Model):
    """
    Product storage table
    """

    size = models.CharField(
        max_length=25,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("product storage size"),
        help_text=_("format: required, unique, max-15"),
    )

    order_field = models.IntegerField(
        default=0,
        verbose_name=_("order field"),
        help_text=_("field used for ordering"),
    )

    class Meta:
        verbose_name = _("storage capacity")
        verbose_name_plural = _("storage capacities")
        ordering = ["order_field"]

    def __str__(self):
        return self.size


class ProductAttribute(models.Model):
    """
    Product attribute table
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("product attribute name"),
        help_text=_("format: required, unique, max-255"),
    )
    description = models.TextField(
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("product attribute description"),
        help_text=_("format: required"),
    )

    def __str__(self):
        return self.name


class ProductType(models.Model):
    """
    Product type table
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("type of product"),
        help_text=_("format: required, unique, max-255"),
    )

    # Hierarchical relationship
    parent = models.ForeignKey(
        'self',  # Points to the same model
        on_delete=models.CASCADE,  
        null=True,  # Allows for top-level categories that have no parent
        blank=True,  # Allows this field to be left blank in forms/admin
        related_name='children'  # Reverse relationship; e.g. if you have a ProductType `laptop`, `laptop.children.all()` will give you all child product types
    )

    product_type_attributes = models.ManyToManyField(
        ProductAttribute,
        related_name="product_type_attributes",
        through="ProductTypeAttribute",
    )

    def __str__(self):
        return self.name

    def get_descendants(self, include_self=True):
        descendants_list = []

        def _get_children(product_type):
            children = ProductType.objects.filter(parent=product_type)
            for child in children:
                _get_children(child)
                descendants_list.append(child.id)

        _get_children(self)

        if include_self:
            descendants_list.append(self.id)

        return descendants_list

    def get_all_attributes(self):
        all_attributes = set()

        # Get attributes of the current product type
        for attr_link in self.producttype.all():
            all_attributes.add(attr_link.product_attribute)

        # Get attributes from parent product types
        current_type = self.parent
        while current_type:
            for attr_link in current_type.producttype.all():
                all_attributes.add(attr_link.product_attribute)
            current_type = current_type.parent

        return all_attributes
    

class ProductAttributeValue(models.Model):
    """
    Product attribute value table
    """

    product_attribute = models.ForeignKey(
        ProductAttribute,
        related_name="product_attribute",
        on_delete=models.PROTECT,
    )
    attribute_value = models.CharField(
        max_length=255,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("attribute value"),
        help_text=_("format: required, max-255"),
    )
    products = models.ManyToManyField(
        Product,
        related_name="attributes",
        verbose_name=_("Associated Products"),
        help_text=_("Select the associated products"),
    )

    def __str__(self):
        return f"{self.product_attribute.name} - {self.attribute_value}"


class ProductInventory(models.Model):
    """
    Product inventory table
    """

    sku = models.CharField(
        max_length=20,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("stock keeping unit"),
        help_text=_("format: required, unique, max-20"),
    )
    upc = models.CharField(
        max_length=12,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("universal product code"),
        help_text=_("format: required, unique, max-12"),
    )
    name = models.TextField(
        unique=False,
        null=True,
        blank=True,
        verbose_name=_("product extra name for SEO"),
        help_text=_("format: not required"),
    )
    seo_feature = models.TextField(
        unique=False,
        null=True,
        blank=True,
        verbose_name=_("product features for SEO"),
        help_text=_("format: not required"),
    )
    product_type = models.ForeignKey(ProductType, related_name="product_type", on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name="product", on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, related_name="brand", on_delete=models.PROTECT)
    color = models.ForeignKey(
        Color, 
        related_name="color", 
        on_delete=models.PROTECT, 
        db_index=True, 
        null=True, 
        blank=True
    )
    storage_size = models.ForeignKey(
        Storage, 
        related_name="storage", 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    attribute_values = models.ManyToManyField(
        ProductAttributeValue,
        related_name="product_attribute_values",
        through="ProductAttributeValues",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("product visibility"),
        help_text=_("format: true=product visible"),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("default selection"),
        help_text=_("format: true=sub product selected"),
    ) 
    retail_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("retail price"),
        help_text=_("format: maximum price 9999999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 9999999.99."),
            },
        },
    )
    store_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("regular store price"),
        help_text=_("format: maximum price 9999999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 9999999.99."),
            },
        },
    )
    discount_store_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("discount regular store price"),
        help_text=_("format: maximum price 9999999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 9999999.99."),
            },
        },
    )
    sale_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        unique=False,
        null=True,
        blank=True,
        verbose_name=_("sale price"),
        help_text=_("format: maximum price 9999999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 9999999.99."),
            },
        },
    )
    condition = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,
        default='used',
        verbose_name=_("product condition"),
        help_text=_("format: select 'New' for new products or 'Used' for UK used products"),
    )
    weight = models.FloatField(
        unique=False,
        null=True,
        blank=True,
        verbose_name=_("product weight"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("date sub-product created"),
        help_text=_("format: Y-m-d H:M:S"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("date sub-product updated"),
        help_text=_("format: Y-m-d H:M:S"),
    )
    
    shipping = models.BooleanField(default=True)
    onsite_pickup = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("product inventory")
        verbose_name_plural = _("product inventories")

    def __str__(self):
        if self.storage_size:
            return f"{self.product.name} - {self.color.name} - {self.storage_size.size}"
        else:
            return f"{self.product.name} - {self.color.name}"

    def get_add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={"sku": self.sku, "quantity": 1, "out": 0})

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={"sku": self.sku})

    def get_remove_single_from_cart_url(self):
        return reverse("remove_single_from_cart", kwargs={"sku": self.sku, "out": 0})


class Media(models.Model):
    """
    The product image table.
    """

    product_inventory = models.ForeignKey(
        ProductInventory,
        on_delete=models.PROTECT,
        related_name="media_product_inventory",
    )

    image = models.ImageField(
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("product image"),
        # upload_to="images/",
        # default="images/default.png",
        help_text=_("format: required, default-default.png"),
    )
    alt_text = models.CharField(
        max_length=255,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("alternative text"),
        help_text=_("format: required, max-255"),
    )
    is_feature = models.BooleanField(
        default=False,
        verbose_name=_("product default image"),
        help_text=_("format: default=False, True=default image"),
    )
    banner = models.BooleanField(
        default=False,
        verbose_name=_("Is Banner"),
        help_text=_("Indicate if this image is used for banner.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("product visibility"),
        help_text=_("format: Y-m-d H:M:S"),
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("date sub-product created"),
        help_text=_("format: Y-m-d H:M:S"),
    )

    def __str__(self):
        return self.product_inventory.sku

    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")


class Stock(models.Model):
    product_inventory = models.OneToOneField(
        ProductInventory,
        related_name="product_inventory",
        on_delete=models.PROTECT,
    )
    last_checked = models.DateTimeField(
        unique=False,
        null=True,
        blank=True,
        verbose_name=_("inventory stock check date"),
        help_text=_("format: Y-m-d H:M:S, null-true, blank-true"),
    )
    units = models.IntegerField(
        default=0,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("units/qty of stock"),
        help_text=_("format: required, default-0"),
    )
    units_sold = models.IntegerField(
        default=0,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("units sold to date"),
        help_text=_("format: required, default-0"),
    )

    def __str__(self):
        return self.product_inventory.sku


class ProductAttributeValues(models.Model):
    """
    Product attribute values link table
    """

    attributevalues = models.ForeignKey(
        "ProductAttributeValue",
        related_name="attributevaluess",
        on_delete=models.PROTECT,
    )
    productinventory = models.ForeignKey(
        ProductInventory,
        related_name="productattributevaluess",
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = (("attributevalues", "productinventory"),)

    def __str__(self):
        return self.productinventory.sku


class ProductTypeAttribute(models.Model):
    """
    Product type attributes link table
    """

    product_type = models.ForeignKey(
        ProductType,
        related_name="producttype",
        on_delete=models.PROTECT,
    )
    product_attribute = models.ForeignKey(
        ProductAttribute,
        related_name="productattribute",
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = (("product_attribute", "product_type"),)

    def __str__(self):
        return self.product_type.name

