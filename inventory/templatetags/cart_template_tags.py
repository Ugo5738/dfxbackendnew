from django import template

from order import models as order_models

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        order_queryset = order_models.Order.objects.filter(user=user, ordered=False)
        if order_queryset.exists():
            return order_queryset[0].products.count()
    return 0


@register.simple_tag
def slug(value):
    return value.product__slug


@register.simple_tag
def get_order_id(value):
    return value.id