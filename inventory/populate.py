from django.core.files import File
from django.db import transaction
from django.utils.text import slugify

from inventory import utils
from inventory.data_store import (brands_list, categories_structure,
                                  other_data, product_attribute_values_data,
                                  product_attributes,
                                  product_type_attributes_data, products,
                                  products_inventory_data)
from inventory.models import (Brand, Category, Color, Media, Product,
                              ProductAttribute, ProductAttributeValue,
                              ProductAttributeValues, ProductInventory,
                              ProductType, ProductTypeAttribute, Stock,
                              Storage)

mobile_memory_sizes = list(utils.MOBILE_STORAGE_CHOICES)
desktop_memory_sizes = list(utils.DESKTOP_STORAGE_DEVICES)


color_list = list(utils.COLOR_CHOICES.keys())


# ------------------ POPULATE CATEGORY MODEL ------------------
def create_category(name, parent=None):
    slug = slugify(name)
    category, created = Category.objects.get_or_create(
        name=name, 
        defaults={
            # 'slug': name.replace(" & ", "_").replace(" ", "_").lower(),
            'slug': slug,
            'parent': parent
        }
    )
    return category

def populate_categories(data, parent=None):
    for category_name, children in data.items():
        cat = create_category(category_name, parent)
        populate_categories(children, cat)

        
# ------------------ POPULATE PRODUCT TYPE MODEL ------------------
def create_product_type(name, parent=None):
    product_type, created = ProductType.objects.get_or_create(
        name=name, 
        defaults={
            'parent': parent
        }
    )
    return product_type

def populate_product_types(categories, parent=None):
    for category, children in categories.items():
        product_type = create_product_type(category, parent)
        populate_product_types(children, product_type)


# ------------------ POPULATE BRAND MODEL ------------------
def create_brand(name):
    brand, created = Brand.objects.get_or_create(name=name)
    return brand

def populate_brands(brands_list):
    for brand_name in brands_list:
        create_brand(brand_name)


# ------------------ POPULATE COLOR MODEL ------------------
def create_color(name, hex_code):
    color, created = Color.objects.get_or_create(name=name, hex_code=hex_code)
    return color

def populate_colors():
    for color, hex_code in utils.COLOR_CHOICES.items():
        create_color(color, hex_code)


# ------------------ POPULATE STORAGE MODEL ------------------
def create_storage(size, order_value):
    storage, created = Storage.objects.get_or_create(size=size, order_field=order_value)
    return storage

def populate_storages():
    for order_value, memory in enumerate(mobile_memory_sizes + desktop_memory_sizes):
        create_storage(memory[0], order_value)


# ------------------ POPULATE PRODUCT ATTRIBUTE MODEL ------------------
def create_product_attribute(name, description):
    attribute, created = ProductAttribute.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    return attribute

def populate_product_attributes():
    for attribute_name, description in product_attributes.items():
        create_product_attribute(attribute_name, description)


# ------------------ POPULATE PRODUCT TYPE ATTRIBUTE MODEL ------------------
def create_product_type_attribute(product_type, attribute):
    product_type_attribute, created = ProductTypeAttribute.objects.get_or_create(
        product_type=product_type,
        product_attribute=attribute
    )
    return product_type_attribute

def populate_product_type_attributes(product_type_data):
    for product_type_name, attributes in product_type_data.items():
        product_type = ProductType.objects.get(name=product_type_name)
        for attribute_name in attributes:
            attribute = ProductAttribute.objects.get(name=attribute_name)
            create_product_type_attribute(product_type, attribute)


# ------------------ POPULATE PRODUCT ATTRIBUTE VALUE MODEL ------------------
def create_product_attribute_value(product, attribute, value, with_product=True):
    product_attribute_value, created = ProductAttributeValue.objects.get_or_create(
        product_attribute=attribute,
        attribute_value=value
    )
    if with_product:
        product_attribute_value.products.add(product)
        product_attribute_value.save()

    return product_attribute_value

# def populate_product_attribute_values(data):
#     for product_name, attributes in data.items():
#         product = Product.objects.get(name=product_name)
#         for attribute_name, value in attributes.items():
#             attribute = ProductAttribute.objects.get(name=attribute_name)
#             create_product_attribute_value(product, attribute, value)


# def populate_product_attribute_values(data):
#     for product_name, attributes in data.items():
#         try:
#             product = Product.objects.get(name=product_name)
#             product_type = product.product_type

#             for attribute_name, value in attributes.items():
#                 attribute = ProductAttribute.objects.get(name=attribute_name)

#                 # Check if the product type supports this attribute
#                 if not ProductTypeAttribute.objects.filter(product_type=product_type, attribute=attribute).exists():
#                     print(f"Error: {attribute_name} is not an allowed attribute for {product_type.name}. Skipping...")
#                     continue

#                 create_product_attribute_value(product, attribute, value)

#         except Product.DoesNotExist:
#             print(f"Error: Product {product_name} does not exist. Skipping...")
#         except ProductAttribute.DoesNotExist:
#             print(f"Error: Attribute {attribute_name} does not exist. Skipping...")


def get_all_attributes_for_category(category):
    """
    Fetch all the attributes for a category and its ancestors.
    """
    attributes = set()

    # Get attributes of the current category
    try:
        product_type = ProductType.objects.get(name=category.name)
        for product_type_attr in product_type.product_type_attributes.all():
            attributes.add(product_type_attr)
    except ProductType.DoesNotExist:
        pass

    # Recursively fetch attributes of parent categories
    if category.parent:
        attributes.update(get_all_attributes_for_category(category.parent))

    return attributes

def populate_product_attribute_values(data):
    for product_name, attributes_data in data.items():
        try:
            product = Product.objects.get(name=product_name)
            categories = product.category.all()
        
            # Collect all attributes for associated categories
            all_allowed_attributes = set()
            for category in categories:
                print(category)
                all_allowed_attributes.update(get_all_attributes_for_category(category))

            # Verify and set attributes for the product
            for attribute_name, value in attributes_data.items():
                attribute = ProductAttribute.objects.get(name=attribute_name) 

                if attribute not in all_allowed_attributes:
                    print(f"Warning: {attribute_name} is not an allowed attribute for {product}'s categories. Category: {category}. Skipping...")
                    continue
                           
                create_product_attribute_value(product, attribute, value)

        except Product.DoesNotExist:
            print(f"Error: Product {product_name} does not exist. Skipping...")
        except ProductAttribute.DoesNotExist:
            print(f"Error: Attribute {attribute_name} does not exist. Skipping...")


def get_product_type_from_path(product_type_path):
    """
    Retrieve the ProductType instance from a path like "Parent > Child > GrandChild".
    Returns None if the given path does not corresponds to what we have in the database.
    """
    categories = [cat.strip() for cat in product_type_path.split(">")]
    current_parent = None

    # Traverse the path to get to the deepest nested ProductType
    for category_name in categories:
        try:
            current_parent = ProductType.objects.get(name=category_name, parent=current_parent)
        except ProductType.DoesNotExist:
            print(f"Warning: ProductType {category_name} does not exist in the path {product_type_path}.")
            return None

    return current_parent


def populate_products(products_data):
    tracking_value = "00100"
    for product_name, product_info in products_data.items():
        product_cat_path = list(products_data[product_name].keys())[0]
        product_cat_name = product_cat_path.split(' > ')[-1]
        product_description = product_info[product_cat_path]
        
        try:
            category = Category.objects.get(name=product_cat_name)
            tracking_value = increment_value(tracking_value)
            web_id = tracking_value
            # Create or update the Product record
            product, created = Product.objects.update_or_create(
                web_id=web_id,
                name=product_name,
                slug=slugify(product_name),
                defaults={
                    'description': product_description
                }
            )

            # Assign the leaf category to the product
            product.category.add(category)
            product.save()

            if created:
                print(f"Product {product_name} was created.")
            else:
                print(f"Product {product_name} was updated.")

        except Category.DoesNotExist:
            print(f"Error: Category {product_cat_name} does not exist. Skipping product {product_name}...")


class ProductInventoryManager:
    def __init__(self):
        self.tracking_value = "0000100"

    def increment_value(self, value: str) -> str:
        int_value = int(value)
        int_value += 1
        # Convert back to string, padding with zeros to maintain the original number of digits
        return str(int_value).zfill(len(value))

    def process_storage(self, storage_size, inventory_data, other_data, product, brand, color, product_type, attributes):
        storage = Storage.objects.get(size=storage_size) if storage_size else None   
        updated_tracking_value = self.increment_value(self.tracking_value)
        self.tracking_value = updated_tracking_value  
        web_id = updated_tracking_value
        updated_sku = "SKU-" + web_id
        updated_upc = "UPC-" + web_id
        print(updated_sku, updated_upc)

        inventory, created = ProductInventory.objects.update_or_create(
            sku=updated_sku,
            defaults={
                'upc': updated_upc,
                'name': inventory_data.get('name'),
                'seo_feature': inventory_data.get('seo_feature'),
                'product_type': product_type,
                'product': product,
                'brand': brand,
                'color': color,
                "is_default": other_data.get("is_default"),
                "retail_price": other_data.get("retail_price"),
                "store_price": other_data.get("store_price"),
                "discount_store_price": other_data.get("discount_store_price"),
                "sale_price": other_data.get("sale_price"),
            }
        )

        if storage:
            inventory.storage_size = storage 
            inventory.save()
        else:
            print("Created without storage")
        
        # Get all valid attributes for this product type
        valid_attributes = {attr.name for attr in product_type.get_all_attributes()}
        print(valid_attributes)
        # Link attributes to the ProductInventory instance
        for attribute_name, value in attributes.items():
            # Ensure the attribute is valid for the product type
            if attribute_name in valid_attributes:
                attribute = ProductAttribute.objects.get(name=attribute_name)

                attribute_value = create_product_attribute_value(None, attribute, value, with_product=False)
                
                # Linking through ProductAttributeValues
                ProductAttributeValues.objects.create(
                    attributevalues=attribute_value,
                    productinventory=inventory
                    )
            else:
                print(f"Warning: {attribute_name} is not an allowed attribute for the product type. Skipping...")
                continue

        file_path = r"inventory\iphone 13.jpg"

        for j in range(4):
            # Open the image file
            with open(file_path, "rb") as f:
                # Create a Django File object
                django_file = File(f)

                if j == 0:
                    is_feature = True
                else:
                    is_feature = False

                image = Media(
                    product_inventory=inventory, 
                    image=django_file,
                    alt_text=product.name + f" {j}",
                    is_feature=is_feature
                )
                image.save()
        
        stock = Stock(product_inventory=inventory, units=20)
        stock.save()

        return inventory

    def create_product_inventory(self, inventory_data, other_data):
        """
        Create or update a ProductInventory instance and link its attributes.
        """
        try:
            product_name = inventory_data.get('product')
            product = Product.objects.get(name=product_name)
            brand = Brand.objects.get(name=inventory_data.get('brand'))
            attributes = inventory_data.get('attributes')

            # Retrieve and assign product_type
            product_type_path = inventory_data.get('product_type')
            # # product_type = None
            # # if product_type_path:
            # #     product_type = get_product_type_from_path(product_type_path)

            product_type_name = product_type_path.split(' > ')[-1]
            product_type = ProductType.objects.get(name=product_type_name)

            for color_name, storage_list in inventory_data['color_storage'].items():
                color = Color.objects.get(name=color_name) if color_name else None

                if storage_list:
                    for storage_size in storage_list:
                        print(f"Checking here {storage_size}") 
                        self.process_storage(
                            storage_size=storage_size, 
                            inventory_data=inventory_data, 
                            other_data=other_data, 
                            product=product, 
                            brand=brand, 
                            color=color, 
                            product_type=product_type, 
                            attributes=attributes
                        )
                else:
                    print("product without storage")
                    self.process_storage(
                        storage_size=None, 
                        inventory_data=inventory_data, 
                        other_data=other_data, 
                        product=product, 
                        brand=brand, 
                        color=color, 
                        product_type=product_type, 
                        attributes=attributes
                    )
            
        except Product.DoesNotExist:
            print(f"Error: Product {product_name} does not exist. Skipping...")
            return None
        except Color.DoesNotExist:
            print(f"Error: Color {color_name} does not exist. Skipping...")
            return None
        except Storage.DoesNotExist:
            print(f"Error: Storage size {storage_size} does not exist. Skipping...")
            return None
        except ProductAttribute.DoesNotExist:
            print(f"Error: Attribute does not exist. Skipping...")
            return None
        except KeyError as ke:
            print(f"Error: Missing key {ke} in inventory data for product {product_name}. Skipping...")
            return None
        except Exception as e:
            # This is a general exception, which will catch all other types of errors
            # While it's useful to have this, be cautious about masking potential issues
            print(f"An unexpected error occurred for product {product_name}: {e}")
            return None


def increment_value(value: str) -> str:
    int_value = int(value)
    int_value += 1
    # Convert back to string, padding with zeros to maintain the original number of digits
    return str(int_value).zfill(len(value))


def save_multiple_product_inventories(products_inventory_data, other_data):
    """
    Save multiple product inventories.
    products_inventory_data: List of dictionaries containing product attributes and inventory data.
    """
    inventories = []
    
    manager = ProductInventoryManager()
    
    for inventory_data in products_inventory_data:
        
        inventory = manager.create_product_inventory(inventory_data, other_data)
    
    return inventories


def deactivate_categories():
    all_categories = Category.objects.all()
    for category in all_categories:
        category.is_active = False
        category.save()


def add_banner_images():
    # Query all inventories, or filter as needed
    all_inventories = ProductInventory.objects.all()

    file_path = r"inventory\banner.jpeg"

    for inventory in all_inventories:
        # Open the image file
        with open(file_path, "rb") as f:
            # Create a Django File object
            django_file = File(f)

            # Create the Media object
            image = Media(
                product_inventory=inventory,
                image=django_file,
                alt_text=inventory.product.name + " Banner",
                is_feature=False,
                banner=True 
            )
            image.save()


# save_multiple_product_inventories(products_inventory_data)


def populate_data():
    # with transaction.atomic():
    populate_categories(categories_structure)
    populate_brands(brands_list)
    populate_colors()
    populate_storages()
    populate_products(products)
    populate_product_attributes()
    populate_product_types(categories_structure)
    populate_product_type_attributes(product_type_attributes_data)
    populate_product_attribute_values(product_attribute_values_data)
    save_multiple_product_inventories(products_inventory_data, other_data)
    add_banner_images()
    deactivate_categories()
    print("Done")


def delete_data():
    Stock.objects.all().delete()
    Media.objects.all().delete()
    ProductAttributeValues.objects.all().delete()
    ProductAttributeValue.objects.all().delete()
    ProductInventory.objects.all().delete()
    Product.objects.all().delete()
    ProductTypeAttribute.objects.all().delete()
    ProductType.objects.all().delete()

    for category in Category.objects.order_by('-level'):
        category.delete()
    # # Category.objects.all().delete()
    
    ProductAttribute.objects.all().delete()
    Color.objects.all().delete()
    Brand.objects.all().delete()
    Storage.objects.all().delete()
    # Payment
    # ShippingOption.objects.all().delete()
    # Address.objects.all().delete()
    # OrderProduct.objects.all().delete()
    # Coupon.objects.all().delete()
    # Payment.objects.all().delete()
    # Order.objects.all().delete()


# # Later, you can use this list to populate the database:

# for data in SAMPLE_DATA:
#     product_inventory = ProductInventory(**data)
#     product_inventory.save()

#     # For ManyToMany fields, you need to add them after the instance has been saved:
#     attribute_value_obj = ProductAttributeValue.objects.get(id=<product attribute value id>)
#     product_inventory.attribute_values.add(attribute_value_obj)