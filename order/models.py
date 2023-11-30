from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from account.models import User
from inventory.models import ProductInventory
from payment.models import Payment


class ShippingOption(models.Model):
    # shipping_option = models.CharField(max_length=3)
    shipping_cost = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("shipping amount"),
        help_text=_("format: maximum amount 9999999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 9999999.99."),
            },
        },
    )


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    country = CountryField(multiple=False)
    zip_code = models.CharField(max_length=200)
    save_info = models.BooleanField(default=False)
    default = models.BooleanField(default=False)
    use_default = models.BooleanField(default=False)
    shipping = models.ForeignKey(ShippingOption, on_delete=models.SET_NULL, blank=True, null=True)
    others = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")

    def __str__(self):
        return self.user.username


class OrderProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductInventory, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.product.name}"

    def get_total_product_price(self):
        return self.quantity * self.product.store_price

    def get_total_product_discount_price(self):
        return self.quantity * self.product.discount_store_price

    def get_amount_saved(self):
        return self.get_total_product_price() - self.get_final_price()

    def get_final_price(self):
        if self.product.discount_store_price:
            return self.get_total_product_discount_price()
        return self.get_total_product_price()


class Coupon(models.Model):
    code = models.CharField(max_length=50)
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("coupon amount"),
        help_text=_("format: maximum amount 9999999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 9999999.99."),
            },
        },
    )

    def __str__(self):
        return self.code


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.email

    def sub_total(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price()
        return total

    def get_total(self):
        total = self.sub_total()
        try:
            if self.coupon:
                total -= self.coupon.amount
            if self.address.shipping:
                total -= self.address.shipping.shipping_cost
            return total
        except:
            return total
 