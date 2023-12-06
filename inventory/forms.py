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
        # Automatically generate slug from name
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = models.Category
        fields = ['name', 'is_active', 'is_trending', 'parent']


class ProductInventoryForm(forms.ModelForm):
    storage_sizes = forms.ModelMultipleChoiceField(
        queryset=models.Storage.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    colors = forms.ModelMultipleChoiceField(
        queryset=models.Color.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(ProductInventoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None

    class Meta:
        model = models.ProductInventory
        exclude = ['sku', 'upc', 'storage_size', 'color', 'shipping', 'onsite_pickup']


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
