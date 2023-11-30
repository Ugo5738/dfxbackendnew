from django.contrib import admin

from order import models


class AddressAdmin(admin.ModelAdmin):
    list_display = ["address", "address2", "country", "zip_code", "default"]


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'sub_total', 'get_total', 'ordered', 'payment_amount', 'coupon_code', 'address_country', 'ordered_date']
    list_filter = ['ordered']
    search_fields = ['user__email']
    
    def payment_amount(self, obj):
        if obj.payment:
            return obj.payment.amount
        return None

    def coupon_code(self, obj):
        if obj.coupon:
            return obj.coupon.code
        return None

    def address_country(self, obj):
        if obj.address:
            return obj.address.country
        return None

    payment_amount.short_description = 'Payment Amount'
    coupon_code.short_description = 'Coupon Code'
    address_country.short_description = 'Address Country'


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'ordered', 'quantity']
    list_filter = ['ordered']
    search_fields = ['user__email']


admin.site.register(models.OrderProduct, OrderProductAdmin)
admin.site.register(models.Coupon)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Address, AddressAdmin)
