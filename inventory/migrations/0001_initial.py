# Generated by Django 4.2.7 on 2024-01-11 23:13

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="format: required, unique, max-255",
                        max_length=255,
                        unique=True,
                        verbose_name="brand name",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="format: required, max-100",
                        max_length=100,
                        verbose_name="category name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="format: required, letters, numbers, underscore, or hyphens",
                        max_length=150,
                        verbose_name="category safe URL",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "is_trending",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Check this field if the category is trending.",
                        verbose_name="is trending",
                    ),
                ),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        help_text="format: not required",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="children",
                        to="inventory.category",
                        verbose_name="parent of category",
                    ),
                ),
            ],
            options={
                "verbose_name": "product category",
                "verbose_name_plural": "product categories",
            },
        ),
        migrations.CreateModel(
            name="Color",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="format: required, unique, max-255",
                        max_length=255,
                        unique=True,
                        verbose_name="color name",
                    ),
                ),
                (
                    "hex_code",
                    models.CharField(
                        help_text="format: required, unique, max-255",
                        max_length=255,
                        unique=True,
                        verbose_name="HEX code",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "web_id",
                    models.CharField(
                        help_text="format: required, unique",
                        max_length=50,
                        unique=True,
                        verbose_name="product website ID",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="format: required, letters, numbers, underscores or hyphens",
                        max_length=255,
                        verbose_name="product safe URL",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="format: required, max-255",
                        max_length=255,
                        verbose_name="product name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="format: required", verbose_name="product description"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="format: true=product visible",
                        verbose_name="product visibility",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="format: Y-m-d H:M:S",
                        verbose_name="date product created",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="format: Y-m-d H:M:S",
                        verbose_name="date product last updated",
                    ),
                ),
                ("category", mptt.fields.TreeManyToManyField(to="inventory.category")),
            ],
        ),
        migrations.CreateModel(
            name="ProductAttribute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="format: required, unique, max-255",
                        max_length=255,
                        unique=True,
                        verbose_name="product attribute name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="format: required",
                        verbose_name="product attribute description",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductAttributeValue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "attribute_value",
                    models.CharField(
                        help_text="format: required, max-255",
                        max_length=255,
                        verbose_name="attribute value",
                    ),
                ),
                (
                    "product_attribute",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="product_attribute",
                        to="inventory.productattribute",
                    ),
                ),
                (
                    "products",
                    models.ManyToManyField(
                        help_text="Select the associated products",
                        related_name="attributes",
                        to="inventory.product",
                        verbose_name="Associated Products",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductAttributeValues",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "attributevalues",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="attributevaluess",
                        to="inventory.productattributevalue",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductInventory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sku",
                    models.CharField(
                        help_text="format: required, unique, max-20",
                        max_length=20,
                        unique=True,
                        verbose_name="stock keeping unit",
                    ),
                ),
                (
                    "upc",
                    models.CharField(
                        help_text="format: required, unique, max-12",
                        max_length=12,
                        unique=True,
                        verbose_name="universal product code",
                    ),
                ),
                (
                    "name",
                    models.TextField(
                        blank=True,
                        help_text="format: not required",
                        null=True,
                        verbose_name="product extra name for SEO",
                    ),
                ),
                (
                    "seo_feature",
                    models.TextField(
                        blank=True,
                        help_text="format: not required",
                        null=True,
                        verbose_name="product features for SEO",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="format: true=product visible",
                        verbose_name="product visibility",
                    ),
                ),
                (
                    "is_default",
                    models.BooleanField(
                        default=False,
                        help_text="format: true=sub product selected",
                        verbose_name="default selection",
                    ),
                ),
                (
                    "retail_price",
                    models.DecimalField(
                        decimal_places=2,
                        error_messages={
                            "name": {
                                "max_length": "the price must be between 0 and 9999999.99."
                            }
                        },
                        help_text="format: maximum price 9999999.99",
                        max_digits=9,
                        verbose_name="retail price",
                    ),
                ),
                (
                    "store_price",
                    models.DecimalField(
                        decimal_places=2,
                        error_messages={
                            "name": {
                                "max_length": "the price must be between 0 and 9999999.99."
                            }
                        },
                        help_text="format: maximum price 9999999.99",
                        max_digits=9,
                        verbose_name="regular store price",
                    ),
                ),
                (
                    "discount_store_price",
                    models.DecimalField(
                        decimal_places=2,
                        error_messages={
                            "name": {
                                "max_length": "the price must be between 0 and 9999999.99."
                            }
                        },
                        help_text="format: maximum price 9999999.99",
                        max_digits=9,
                        verbose_name="discount regular store price",
                    ),
                ),
                (
                    "sale_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        error_messages={
                            "name": {
                                "max_length": "the price must be between 0 and 9999999.99."
                            }
                        },
                        help_text="format: maximum price 9999999.99",
                        max_digits=9,
                        null=True,
                        verbose_name="sale price",
                    ),
                ),
                (
                    "condition",
                    models.CharField(
                        choices=[("new", "New"), ("used", "Used")],
                        default="used",
                        help_text="format: select 'New' for new products or 'Used' for UK used products",
                        max_length=10,
                        verbose_name="product condition",
                    ),
                ),
                (
                    "weight",
                    models.FloatField(
                        blank=True, null=True, verbose_name="product weight"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="format: Y-m-d H:M:S",
                        verbose_name="date sub-product created",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="format: Y-m-d H:M:S",
                        verbose_name="date sub-product updated",
                    ),
                ),
                ("shipping", models.BooleanField(default=True)),
                ("onsite_pickup", models.BooleanField(default=True)),
                (
                    "attribute_values",
                    models.ManyToManyField(
                        related_name="product_attribute_values",
                        through="inventory.ProductAttributeValues",
                        to="inventory.productattributevalue",
                    ),
                ),
                (
                    "brand",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="brand",
                        to="inventory.brand",
                    ),
                ),
                (
                    "color",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="color",
                        to="inventory.color",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="product",
                        to="inventory.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "product inventory",
                "verbose_name_plural": "product inventories",
            },
        ),
        migrations.CreateModel(
            name="ProductType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="format: required, unique, max-255",
                        max_length=255,
                        unique=True,
                        verbose_name="type of product",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="inventory.producttype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Storage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "size",
                    models.CharField(
                        help_text="format: required, unique, max-15",
                        max_length=25,
                        unique=True,
                        verbose_name="product storage size",
                    ),
                ),
                (
                    "order_field",
                    models.IntegerField(
                        default=0,
                        help_text="field used for ordering",
                        verbose_name="order field",
                    ),
                ),
            ],
            options={
                "verbose_name": "storage capacity",
                "verbose_name_plural": "storage capacities",
                "ordering": ["order_field"],
            },
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_checked",
                    models.DateTimeField(
                        blank=True,
                        help_text="format: Y-m-d H:M:S, null-true, blank-true",
                        null=True,
                        verbose_name="inventory stock check date",
                    ),
                ),
                (
                    "units",
                    models.IntegerField(
                        default=0,
                        help_text="format: required, default-0",
                        verbose_name="units/qty of stock",
                    ),
                ),
                (
                    "units_sold",
                    models.IntegerField(
                        default=0,
                        help_text="format: required, default-0",
                        verbose_name="units sold to date",
                    ),
                ),
                (
                    "product_inventory",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="product_inventory",
                        to="inventory.productinventory",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductTypeAttribute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product_attribute",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="productattribute",
                        to="inventory.productattribute",
                    ),
                ),
                (
                    "product_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="producttype",
                        to="inventory.producttype",
                    ),
                ),
            ],
            options={
                "unique_together": {("product_attribute", "product_type")},
            },
        ),
        migrations.AddField(
            model_name="producttype",
            name="product_type_attributes",
            field=models.ManyToManyField(
                related_name="product_type_attributes",
                through="inventory.ProductTypeAttribute",
                to="inventory.productattribute",
            ),
        ),
        migrations.AddField(
            model_name="productinventory",
            name="product_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_type",
                to="inventory.producttype",
            ),
        ),
        migrations.AddField(
            model_name="productinventory",
            name="storage_size",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="storage",
                to="inventory.storage",
            ),
        ),
        migrations.AddField(
            model_name="productattributevalues",
            name="productinventory",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="productattributevaluess",
                to="inventory.productinventory",
            ),
        ),
        migrations.CreateModel(
            name="Media",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="format: required, default-default.png",
                        upload_to="",
                        verbose_name="product image",
                    ),
                ),
                (
                    "alt_text",
                    models.CharField(
                        help_text="format: required, max-255",
                        max_length=255,
                        verbose_name="alternative text",
                    ),
                ),
                (
                    "is_feature",
                    models.BooleanField(
                        default=False,
                        help_text="format: default=False, True=default image",
                        verbose_name="product default image",
                    ),
                ),
                (
                    "banner",
                    models.BooleanField(
                        default=False,
                        help_text="Indicate if this image is used for banner.",
                        verbose_name="Is Banner",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="format: Y-m-d H:M:S",
                        verbose_name="product visibility",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="format: Y-m-d H:M:S",
                        verbose_name="date sub-product created",
                    ),
                ),
                (
                    "product_inventory",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="media_product_inventory",
                        to="inventory.productinventory",
                    ),
                ),
            ],
            options={
                "verbose_name": "product image",
                "verbose_name_plural": "product images",
            },
        ),
        migrations.AlterUniqueTogether(
            name="productattributevalues",
            unique_together={("attributevalues", "productinventory")},
        ),
    ]
