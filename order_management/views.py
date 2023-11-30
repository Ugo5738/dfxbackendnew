import re

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView, View

from inventory import models as inventory_models
from order import models as order_models

from . import forms


# ======================== INVENTORY MANAGEMENT ========================
class DashboardView(View):
    template_name = "inventory/i-ecommerce-dashboard.html"

    def get(self, request, *args, **kwargs):
        orders = order_models.Order.objects.all()
        orders_with_totals = []

        for order in orders:
            order_total = order.get_total()
            orders_with_totals.append((order, order_total))

        context = {
            "orders_with_totals": orders_with_totals,
        }

        return render(request, self.template_name, context)


class InventoryOrderListView(View):
    template_name = "inventory/i-order-list.html"

    def get(self, request, *args, **kwargs):
        orders = order_models.Order.objects.all()

        context = {
            "orders": orders,
            "inventory_order_list": reverse("inventory_order_list")
        }
        return render(request, self.template_name, context)


class InventoryProductListView(View):
    template_name = "inventory/i-products-list.html"

    def get(self, request, *args, **kwargs):
        categories = inventory_models.Category.objects.all()
        product_inventories = inventory_models.ProductInventory.objects.all()
        context = {
            "categories": categories,
            "product_inventories": product_inventories,
            "inventory_product_list": reverse("inventory_product_list")
        }
        return render(request, self.template_name, context)


class InventoryProductView(View):
    template_name = "inventory/i-products.html"

    def get(self, request, *args, **kwargs):
        sku = kwargs["sku"]
        product_inventory_item = (inventory_models.ProductInventory.objects.filter(sku=sku).values(
                "id",
                "sku",
                "upc",
                "product__name",
                "product__slug",
                "product__description",
                "store_price",
                "product__category__name",
                "brand__name",
            )
        ).get()

        product_colors = inventory_models.Product.objects.filter(product__sku=sku).values(
            "product__color__name",
            "product__color__hex_code",
        )
        # print(product_colors)

        product_inventory_colors = inventory_models.ProductInventory.objects.filter(sku=sku).values(
                    "color__name",
                    "color__hex_code",
                )

        images = inventory_models.Media.objects.filter(product_inventory=product_inventory_item["id"]).all()

        product_attributes = (
            inventory_models.ProductInventory.objects.filter(product__slug=product_inventory_item["product__slug"])
            .distinct()
            .values(
                "attribute_values__product_attribute__name",
                "attribute_values__attribute_value",
            )
        )

        product_type_attributes = (
            inventory_models.ProductTypeAttribute.objects.filter(product_type__product_type__product__slug=product_inventory_item["product__slug"])
            .distinct()
            .values("product_attribute__name")
        )

        attribute_names = [
            attribute["attribute_values__product_attribute__name"] for attribute in product_attributes
        ]

        context = {
            "product_inventory_item": product_inventory_item,
            "attribute_names": attribute_names,
            "product_attributes": product_attributes,
            "product_type_attributes": product_type_attributes,
            "images": images,
            "product_colors": product_colors,
            "product_inventory_colors": product_inventory_colors,
        }
        return render(request, self.template_name, context)


class InventoryProductEditView(View):
    template_name = "inventory/i-products-edit.html"

    def get(self, request, *args, **kwargs):
        sku = kwargs['sku']
        product_inventory_item = inventory_models.ProductInventory.objects.filter(sku=sku).first()
        context = {"product_inventory_item": product_inventory_item}
        return render(request, self.template_name, context)
# ======================== INVENTORY MANAGEMENT ========================


# ==================== UPDATING DATA ====================
def remove_special_characters(string):
    return re.sub(r"[^\w\s]", "", string)


class UpdateView(View):
    template_name = "updateform.html"

    def get(self, request, *args, **kwargs):
        form = forms.ProductInventoryForm()
        context = {
            "form": form,
            "product_inventory": True,
        }
        # inventory_models.Stock.objects.all().delete()
        # inventory_models.Media.objects.all().delete()
        # inventory_models.ProductAttributeValues.objects.all().delete()
        # inventory_models.ProductAttributeValue.objects.all().delete()
        # inventory_models.ProductInventory.objects.all().delete()
        # inventory_models.Product.objects.all().delete()
        # inventory_models.ProductTypeAttribute.objects.all().delete()
        # inventory_models.ProductType.objects.all().delete()
        # inventory_models.Category.objects.all().delete()
        # inventory_models.ProductAttribute.objects.all().delete()
        # inventory_models.Color.objects.all().delete()
        # inventory_models.Brand.objects.all().delete()
        # inventory_models.Storage.objects.all().delete()
        # # Payment
        # payment_models.ShippingOption.objects.all().delete()
        # order_models.Address.objects.all().delete()
        # order_models.OrderProduct.objects.all().delete()
        # order_models.Coupon.objects.all().delete()
        # payment_models.Payment.objects.all().delete()
        # order_models.Order.objects.all().delete()

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.ProductInventoryForm(request.POST or None, request.FILES)
        
        if form.is_valid():
            # product
            product_name = form.cleaned_data.get("product")
            new_product = inventory_models.Product.objects.get(name=product_name)
            
            # product type
            product_type_name = form.cleaned_data.get("product_type_name")
            product_type, product_type_created = inventory_models.ProductType.objects.get_or_create(
                name=product_type_name
            )
            if product_type_created:
                product_type.save()

            # Brand
            brand_name = form.cleaned_data.get("brand_name")
            product_brand = inventory_models.Brand.objects.get(name=brand_name)

            # Color
            color_name = form.cleaned_data.get("color_name")
            product_color = inventory_models.Color.objects.get(name=color_name)
            
            # Storage
            storage_size = form.cleaned_data.get("storage_size")
            
            # Product Inventory
            product_inventory_name = form.cleaned_data.get("inventory_name")
            product_inventory_seo_feature = form.cleaned_data.get("inventory_seo_feature")
            product_default = form.cleaned_data.get("product_default")
            product_retail_price = 20 # form.cleaned_data.get("product_retail_price")
            product_store_price = 30 # form.cleaned_data.get("product_store_price")
            product_discount_store_price = 28 # form.cleaned_data.get("product_discount_store_price")
            product_sale_price = 25 # form.cleaned_data.get("product_sale_price")
            weight = form.cleaned_data.get("weight")
            stock_units = 20 # form.cleaned_data.get("stock_units")
            product_condition = form.cleaned_data.get("condition")
            
            if inventory_models.ProductInventory.objects.last():
                latest_inventory = inventory_models.ProductInventory.objects.last()

                latest_inventory_sku = "sku-000" + str(int(latest_inventory.sku.split('-')[1]) + 1)
                latest_inventory_upc = "upc-000" + str(int(latest_inventory.upc.split('-')[1]) + 1)
            else:
                latest_inventory_sku = "sku-0000"
                latest_inventory_upc = "upc-0000"

            if storage_size:
                product_storage_size = inventory_models.Storage.objects.get(size=storage_size)

                new_inventory = inventory_models.ProductInventory(
                    sku=latest_inventory_sku,
                    upc=latest_inventory_upc,
                    name=product_inventory_name,
                    seo_feature=product_inventory_seo_feature,
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
                    condition=product_condition,
                )
            else: 
                new_inventory = inventory_models.ProductInventory(
                    sku=latest_inventory_sku,
                    upc=latest_inventory_upc,
                    name=product_inventory_name,
                    seo_feature=product_inventory_seo_feature,
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
                    condition=product_condition,
                )

            new_inventory.save()

            # product_attribute_value = []
            # for field_name, attribute_value in form.cleaned_data.items():
            #     if field_name.startswith("attribute_"):
            #         attribute_id = field_name.split("_")[1]
            #         attribute = models.ProductAttribute.objects.get(id=attribute_id)
            #         attribute_value_obj = models.ProductAttributeValue(
            #             product_attribute=attribute,
            #             attribute_value=attribute_value
            #         )
            #         attribute_value_obj.save()
            #         product_attribute_value.append(attribute_value_obj)
            # if product_attribute_value:
            #     new_inventory.attribute_values.add(product_attribute_value)
            #     new_inventory.save()

            # Product Stock
            product_stock = inventory_models.Stock(product_inventory=new_inventory, units=stock_units)
            product_stock.save()

            # Product Media
            image_1 = form.cleaned_data.get("image_1")
            image_2 = form.cleaned_data.get("image_2")
            image_3 = form.cleaned_data.get("image_3")
            image_1_name = form.cleaned_data.get("image_1_name")
            image_2_name = form.cleaned_data.get("image_2_name")
            image_3_name = form.cleaned_data.get("image_3_name")

            if image_1:
                image_1 = inventory_models.Media(
                    product_inventory=new_inventory, 
                    image=image_1, 
                    alt_text=image_1_name, 
                    is_feature=True
                )
                image_1.save()
            if image_2:
                image_2 = inventory_models.Media(
                    product_inventory=new_inventory, 
                    image=image_2, 
                    alt_text=image_2_name, 
                    is_feature=False
                )
                image_2.save()
            if image_3:
                image_3 = inventory_models.Media(
                    product_inventory=new_inventory, 
                    image=image_3, 
                    alt_text=image_3_name, 
                    is_feature=False
                )
                image_3.save()
        else:
            print("form not valid")
        return redirect("update_button")# , update_type="product_inventory")
    

class PriceUpdateView(View):
    template_name = "updateform.html"

    def get(self, request, *args, **kwargs):

        form = forms.PriceForm()
        context = {
            "form": form,
            "product_price": True,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.PriceForm(request.POST or None, request.FILES)
        
        if form.is_valid():
            product_sku = form.cleaned_data.get("product_inventory")
            product_retail_price = form.cleaned_data.get("product_retail_price")
            product_store_price = form.cleaned_data.get("product_store_price")
            product_discount_store_price = form.cleaned_data.get("product_discount_store_price")
            product_sale_price = form.cleaned_data.get("product_sale_price")
                        
            parent_inventory_sku = inventory_models.ProductInventory.objects.get(sku=product_sku)
            parent_inventory_sku.retail_price = product_retail_price
            parent_inventory_sku.store_price = product_store_price
            parent_inventory_sku.discount_store_price = product_discount_store_price
            parent_inventory_sku.sale_price = product_sale_price
            parent_inventory_sku.save()
        else:
            print("form not valid")
        return redirect("update_button") #, update_type="product_price")


class ProductCategoryCreateView(View):
    template_name = "updateform.html"

    def get(self, request, *args, **kwargs):

        form = forms.ProductForm()
        context = {
            "form": form,
            "product_category": True,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.ProductForm(request.POST or None, request.FILES)
        
        if form.is_valid():
            # CATEGORY
            parent_or_category_name = form.cleaned_data.get("parent_or_existing_category")
            category_name = form.cleaned_data.get("category")
                        
            parent_category = inventory_models.Category.objects.get(name=parent_or_category_name)
            category = inventory_models.Category.objects.get(name=category_name)

            if category:
                category_slug = remove_special_characters(category_name).replace(" ", "-")         
                category, created = inventory_models.Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'slug': category_slug,
                    }
                )

            # PRODUCT
            product_name = form.cleaned_data.get("product_name")
            product_description = form.cleaned_data.get("product_description")
            product_slug = remove_special_characters(product_name).replace(" ", "-")
            
            if inventory_models.Product.objects.last():
                latest_product = inventory_models.Product.objects.last()
                latest_product_web_id = latest_product.web_id
                product_web_id = "dfx-web-00" + str(int(latest_product_web_id.split('-')[-1]) + 1)
            else: 
                product_web_id = 'dfx-web-000'
            
            new_product = inventory_models.Product(
                web_id=product_web_id,
                slug=product_slug,
                name=product_name,
                description=product_description,
            )
            new_product.save()
            if category:
                new_product.category.set([category])
            else:
                new_product.category.set([parent_category])
        else:
            print("form not valid")
        return redirect("update_button")# , update_type="product_category")


class ProductAttributeCreateView(View):
    template_name = "updateform.html"

    def get(self, request, *args, **kwargs):
        form = forms.AttributeForm()
        context = {
            "form": form,
            "product_attribute": True, 
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.AttributeForm(request.POST or None, request.FILES)
        
        if form.is_valid():
            product = form.cleaned_data.get("product")
            product_attribute_1 = form.cleaned_data.get("attribute_1")
            product_attribute_2 = form.cleaned_data.get("attribute_2")
            product_attribute_3 = form.cleaned_data.get("attribute_3")
            product_attribute_4 = form.cleaned_data.get("attribute_4")
            product_attribute_5 = form.cleaned_data.get("attribute_5")
            product_attribute_6 = form.cleaned_data.get("attribute_6")
            
            product_inventories = inventory_models.ProductInventory.objects.filter(product__name=product)
            if product_attribute_1:
                product_attr_1 = product_attribute_1.split("->")[-1].strip()  
                product_attr_obj_1 = inventory_models.ProductAttributeValue.objects.filter(attribute_value=product_attr_1).first()

                for product_inventory in product_inventories:
                    product_attribute_values = inventory_models.ProductAttributeValues(
                        attributevalues=product_attr_obj_1,
                        productinventory=product_inventory
                    )
                    product_attribute_values.save()

            if product_attribute_2:
                product_attr_2 = product_attribute_2.split("->")[-1].strip()  
                product_attr_obj_2 = inventory_models.ProductAttributeValue.objects.filter(attribute_value=product_attr_2).first()

                for product_inventory in product_inventories:
                    product_attribute_values = inventory_models.ProductAttributeValues(
                        attributevalues=product_attr_obj_2,
                        productinventory=product_inventory
                    )
                    product_attribute_values.save()

            if product_attribute_3:
                product_attr_3 = product_attribute_3.split("->")[-1].strip()  
                product_attr_obj_3 = inventory_models.ProductAttributeValue.objects.filter(attribute_value=product_attr_3).first()

                for product_inventory in product_inventories:
                    product_attribute_values = inventory_models.ProductAttributeValues(
                        attributevalues=product_attr_obj_3,
                        productinventory=product_inventory
                    )
                    product_attribute_values.save()
            
            if product_attribute_4:
                product_attr_4 = product_attribute_4.split("->")[-1].strip()  
                product_attr_obj_4 = inventory_models.ProductAttributeValue.objects.filter(attribute_value=product_attr_4).first()

                for product_inventory in product_inventories:
                    product_attribute_values = inventory_models.ProductAttributeValues(
                        attributevalues=product_attr_obj_4,
                        productinventory=product_inventory
                    )
                    product_attribute_values.save()
            
            if product_attribute_5:
                product_attr_5 = product_attribute_5.split("->")[-1].strip()  
                product_attr_obj_5 = inventory_models.ProductAttributeValue.objects.filter(attribute_value=product_attr_5).first()

                for product_inventory in product_inventories:
                    product_attribute_values = inventory_models.ProductAttributeValues(
                        attributevalues=product_attr_obj_5,
                        productinventory=product_inventory
                    )
                    product_attribute_values.save()

            if product_attribute_6:
                product_attr_6 = product_attribute_6.split("->")[-1].strip()  
                product_attr_obj_6 = inventory_models.ProductAttributeValue.objects.filter(attribute_value=product_attr_6).first()

                for product_inventory in product_inventories:
                    product_attribute_values = inventory_models.ProductAttributeValues(
                        attributevalues=product_attr_obj_6,
                        productinventory=product_inventory
                    )
                    product_attribute_values.save()

        else:
            print("form not valid")
        return redirect("update_button")#, update_type="product_price")


class UpdateButtonsView(TemplateView):
    template_name = "update_buttons.html"
    

class UpdateDoneView(TemplateView):
    template_name = "update_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        update_type = self.kwargs.get('update_type')
        context['update_type'] = update_type
        return context
# ==================== UPDATING DATA ====================