from django import forms
from django.utils.text import slugify

from inventory import models


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None

    class Meta:
        model = models.Product
        fields = ['name', 'description', 'category', 'is_active']


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None

    def save(self, commit=True):
        instance = super(CategoryForm, self).save(commit=False)
        instance.slug = slugify(instance.name)

        if commit:
            instance.save()
            # Handle the parent for ProductType
            product_type_parent = None
            if instance.parent:
                # Try to get the corresponding ProductType for the parent Category, if it exists
                product_type_parent = models.ProductType.objects.filter(name=instance.parent.name).first()

            # Create or update the corresponding ProductType
            models.ProductType.objects.update_or_create(
                name=instance.name,
                defaults={'parent': product_type_parent}
            )

        return instance

    class Meta:
        model = models.Category
        fields = ['name', 'is_active', 'is_trending', 'parent']


class ProductPriceForm(forms.Form):
    storage_size = forms.ModelChoiceField(queryset=models.Storage.objects.all(), required=False)
    color = forms.ModelChoiceField(queryset=models.Color.objects.all(), required=False)
    image_1 = forms.ImageField(required=False, label='Image 1')
    image_1_name = forms.CharField(required=False, label='Image 1 Alt Text')
    image_2 = forms.ImageField(required=False, label='Image 2')
    image_2_name = forms.CharField(required=False, label='Image 2 Alt Text')
    image_3 = forms.ImageField(required=False, label='Image 3')
    image_3_name = forms.CharField(required=False, label='Image 3 Alt Text')
    retail_price = forms.DecimalField(max_digits=9, decimal_places=2)
    store_price = forms.DecimalField(max_digits=9, decimal_places=2)
    discount_store_price = forms.DecimalField(max_digits=9, decimal_places=2)
    sale_price = forms.DecimalField(max_digits=9, decimal_places=2, required=False)

ProductPriceFormSet = forms.formset_factory(ProductPriceForm, extra=0)


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        attrs = attrs or {}
        attrs.update({'class': 'storage-size' if name == 'storage_sizes' else 'color'})
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        option['attrs']['data-name'] = label
        return option
    

class ProductInventoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductInventoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None

    storage_sizes = forms.ModelMultipleChoiceField(
        queryset=models.Storage.objects.all(),
        widget=CustomCheckboxSelectMultiple,
        required=False
    )
    colors = forms.ModelMultipleChoiceField(
        queryset=models.Color.objects.all(),
        widget=CustomCheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = models.ProductInventory
        exclude = [
            'sku', 'upc', 'storage_size', 'color', 'attribute_values', 
            'retail_price', 'store_price', 'discount_store_price', 'sale_price',
            'shipping', 'onsite_pickup'
        ]


class ProductAttributeValueForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=models.Product.objects.all())

    class Meta:
        model = models.ProductAttributeValue
        fields = ['product_attribute', 'attribute_value', 'product']

    def save(self, commit=True):
        # Overriding save method to handle the linkage
        product_attribute_value = super().save(commit=False)
        
        # Don't save yet if commit is False
        if commit:
            product_attribute_value.save()

            selected_product = self.cleaned_data['product']
            # Linking this attribute value to all inventories of the selected product
            for inventory in models.ProductInventory.objects.filter(product=selected_product):
                inventory.attribute_values.add(product_attribute_value)

        return product_attribute_value
