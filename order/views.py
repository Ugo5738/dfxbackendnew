from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from inventory.models import ProductInventory, Stock
from order.models import Coupon, Order, OrderProduct
from order.serializers import OrderSerializer


# ------------------------- ORDERS -------------------------
class AddToCartAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        user = request.user
        sku = kwargs.get('sku')  # replace with your actual SKU parameter
        quantity = int(kwargs.get('quantity', 1))

        # Check if quantity exceeds 3
        if quantity > 3:
            return Response({'error': 'Cannot add more than 3 of the same item at a time'})
        
        # Find the corresponding product inventory and stock
        try:
            product = ProductInventory.objects.get(sku=sku)
            stock = Stock.objects.get(product_inventory=product)
        except ProductInventory.DoesNotExist:
            return Response({'error': 'Product with this SKU does not exist.'})
        except Stock.DoesNotExist:
            return Response({'error': 'Stock information is missing.'})

        # Fetch or create an 'Order' object for the current user
        order, _ = Order.objects.get_or_create(
            user=user, 
            ordered=False,
            # defaults={'ordered_date': timezone.now()}
        )

        # Check if the product is already in the cart
        order_product, created = OrderProduct.objects.get_or_create(
            user=user,
            product=product,
            ordered=False,
        )

        # Check available units in stock
        if created:
            if stock.units < quantity:
                return Response({'error': 'Not enough items in stock'})
            order_product.quantity = quantity
            order_product.save()
            stock.units -= quantity  # Decrement units in stock
            stock.units_sold += quantity  # Increment units sold
            stock.save()
            order.products.add(order_product)
        else:
            new_quantity = order_product.quantity + quantity
            if new_quantity > 3:
                return Response({'error': 'Cannot add more than 3 of the same item at a time'})
            if stock.units < new_quantity:
                return Response({'error': 'Not enough items in stock'})
            order_product.quantity = new_quantity
            order_product.save()
            stock.units -= quantity  # Decrement units in stock
            stock.units_sold += quantity  # Increment units sold
            stock.save()

        # Serialize the order
        serializer = OrderSerializer(order)

        return Response({'message': 'Item added to cart', 'order': serializer.data}, status=status.HTTP_201_CREATED)


class RemoveFromCartAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        user = request.user
        sku = kwargs.get('sku')  # replace with your actual SKU parameter

        try:
            product = ProductInventory.objects.get(sku=sku)
            stock = Stock.objects.get(product_inventory=product)
        except ProductInventory.DoesNotExist:
            return Response({'error': 'Product with this SKU does not exist.'})
        except Stock.DoesNotExist:
            return Response({'error': 'Stock information is missing.'})

        try:
            order = Order.objects.get(user=user, ordered=False)
        except Order.DoesNotExist:
            return Response({'error': 'You do not have an active order'})

        try:
            order_product = OrderProduct.objects.get(
                user=user, 
                product=product, 
                ordered=False
            )
        except OrderProduct.DoesNotExist:
            return Response({'error': 'This item was not in your cart'})

        stock.units += order_product.quantity
        stock.units_sold -= order_product.quantity
        stock.save()
        order.products.remove(order_product)
        order_product.delete()

        serializer = OrderSerializer(order)
        return Response({'message': 'Item removed from cart', 'order': serializer.data}, status=status.HTTP_200_OK)


class RemoveSingleFromCartAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        user = request.user
        sku = kwargs.get('sku')  # replace with your actual SKU parameter

        try:
            product = ProductInventory.objects.get(sku=sku)
            stock = Stock.objects.get(product_inventory=product)
        except ProductInventory.DoesNotExist:
            return Response({'error': 'Product with this SKU does not exist.'})
        except Stock.DoesNotExist:
            return Response({'error': 'Stock information is missing.'})

        try:
            order = Order.objects.get(user=user, ordered=False)
        except Order.DoesNotExist:
            return Response({'error': 'You do not have an active order'})

        try:
            order_product = OrderProduct.objects.get(
                user=user, 
                product=product, 
                ordered=False
            )
        except OrderProduct.DoesNotExist:
            return Response({'error': 'This item was not in your cart'})

        if order_product.quantity > 1:
            order_product.quantity -= 1
            order_product.save()
        else:
            return Response({'error': 'Only one item in cart, use remove from cart to delete the item.'})
        
        # Increment stock since we're removing one item
        stock.units += 1  
        stock.units_sold -= 1  
        stock.save()

        serializer = OrderSerializer(order)
        return Response({'message': 'Removed single item from cart', 'order': serializer.data}, status=status.HTTP_200_OK)


class OrderSummaryAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            order = Order.objects.get(user=user, ordered=False)
        except Order.DoesNotExist:
            return Response({'error': 'You do not have an active order'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the order
        serializer = OrderSerializer(order)

        return Response({'order_summary': serializer.data}, status=status.HTTP_200_OK)
    

class ApplyCouponAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get("order_id")
        coupon_code = request.data.get("coupon_code")

        try:
            order = Order.objects.get(id=order_id, user=user, ordered=False)
        except Order.DoesNotExist:
            return Response({"error": "You do not have an active order"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the coupon (e.g., check if it's expired)
        # ...

        # Apply the coupon to the order
        order.coupon = coupon
        order.save()

        serializer = OrderSerializer(order)
        return Response({"message": "Coupon applied", "order": serializer.data}, status=status.HTTP_200_OK)
# ------------------------- ORDERS -------------------------


# note to take up
# boolean value for shipping and onsite pickup
