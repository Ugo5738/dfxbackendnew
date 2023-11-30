from django import forms

from inventory import models as inventory_models

storage_choices = [(storage_size.size, storage_size.size) for storage_size in inventory_models.Storage.objects.all()]
product_choices = [(product.name, product.name) for product in inventory_models.Product.objects.all()]
attribute_choices = [(
        f"{attribute.product_attribute.name} -> {attribute.attribute_value}",
        f"{attribute.product_attribute.name} -> {attribute.attribute_value}"
    )
    for attribute in inventory_models.ProductAttributeValue.objects.all()
]


class ProductInventoryForm(forms.Form):
    # def __init__(self, *args, **kwargs):
    #     super(ProductInventoryForm, self).__init__(*args, **kwargs)
    #     attributes = models.ProductAttribute.objects.all()
    #     for attribute in attributes:
    #         field_name = f"attribute_{attribute.id}"
    #         field_label = attribute.name
    #         self.fields[field_name] = forms.CharField(
    #             label=field_label,
    #             widget=forms.TextInput(
    #                 attrs={
    #                     "class": "form-control ms-2 mb-3",
    #                     "placeholder": f"Enter {field_label} here",
    #                 }
    #             ),
    #             max_length=255,
    #             required=True,
    #         )
    inventory_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Enter Extra Inventory Name here to help with SEO",
            }
        ),
        max_length=50,
        required=False,
    )
    inventory_seo_feature = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Enter Extra Inventory Features here to help with SEO",
            }
        ),
        max_length=500,
        required=False,
    )
    product = forms.ChoiceField(
        widget=forms.Select( 
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product here",
            }
        ),
        choices=[(product.name, product.name) for product in inventory_models.Product.objects.all()],
        required=True,
    )

    # BRAND
    brand_name = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product Brand here",
            }
        ),
        choices=[(brand.name, brand.name) for brand in inventory_models.Brand.objects.all()],
        required=True,
    )

    condition = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product Condition here",
            }
        ),
        choices=[('new', 'New'), ('used', 'UK Used')],
        required=True,
    )

    # COLOR
    color_name = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product Color here",
            }
        ),
        choices=[(color.name, color.name) for color in inventory_models.Color.objects.all()],
        required=True,
    )

    # STORAGE
    storage_size = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Storage Size here",
            }
        ),
        choices=[("", "---------")] + storage_choices, 
        required=False,
    )
    
    # PRODUCT TYPE
    product_type_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Enter Product Type here",
            }
        ),
        max_length=50,
        required=True,
    )
    
    # PRODUCT INVENTORY
    product_default = forms.BooleanField(
        widget=forms.CheckboxInput(
          attrs={
              "class": "form-check-input ms-3 mb-3 p-2",
          },
        ),
        required=False,
    )
    weight = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Enter Product Weight here",
            }
        ),
        max_length=50,
        required=False,
    )

    image_1 = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Front Image here",
                "accept": "image/*",
            }
        ),
        required=True,
    )

    image_1_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Front Image name",
            }
        ),
        max_length=100,
        required=False,
    )

    image_2 = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Side Image here",
                "accept": "image/*",
            }
        ),
        required=True,
    )

    image_2_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Side Image name",
            }
        ),
        max_length=100,
        required=False,
    )

    image_3 = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Back Image here",
                "accept": "image/*",
            }
        ),
        required=True,
    )

    image_3_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Back Image name",
            }
        ),
        max_length=100,
        required=False,
    )

    stock_units = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Enter Product Default here",
            }
        ),
        max_length=50,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(ProductInventoryForm, self).__init__(*args, **kwargs)


class AttributeForm(forms.Form):
    product = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product here",
            }
        ),
        choices=product_choices[::-1],
        required=True,
    )

    attribute_1 = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product here",
            }
        ),
        choices=[("", "----")] + attribute_choices[::-1],
        required=True,
    )

    attribute_2 = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product here",
            }
        ),
        choices=[("", "----")] + attribute_choices[::-1],
        required=False,
    )
    
    attribute_3 = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product here",
            }
        ),
        choices=[("", "----")] + attribute_choices[::-1],
        required=False,
    )

    attribute_4 = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product here",
            }
        ),
        choices=[("", "----")] + attribute_choices[::-1],
        required=False,
    )
    
    attribute_5 = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product here",
            }
        ),
        choices=[("", "----")] + attribute_choices[::-1],
        required=False,
    )

    attribute_6 = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Select Product here",
            }
        ),
        choices=[("", "----")] + attribute_choices[::-1],
        required=False,
    )

