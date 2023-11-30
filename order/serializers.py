from rest_framework import serializers

from inventory.models import Stock
from inventory.serializers import ProductInventorySerializer
from order.models import Address, Order, OrderProduct, ShippingOption


class ShippingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingOption
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductInventorySerializer(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ('id', 'ordered', 'quantity', 'product')


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)
    sub_total = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'products', 'ordered', 'start_date', 'ordered_date', 'user', 'address', 'payment', 'coupon', 'sub_total', 'total')

    def get_sub_total(self, obj):
        return obj.sub_total()

    def get_total(self, obj):
        return obj.get_total()
