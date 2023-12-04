import datetime
import hashlib
import hmac
import json
import os
import random

from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import User
from inventory.models import Stock
from order.models import Order
from payment.models import Payment

# # Create your views here.
# class ManualPayment(LoginRequiredMixin, TemplateView):
#         template_name = "payment/manual_payment.html"



class InitiatePayment(APIView):
    permission_classes = [IsAuthenticated]

    # def generate_tx_ref(self):
    #     """Generate a unique transaction reference"""
    #     characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    #     result = "".join(random.choice(characters) for i in range(15))
    #     return "dfx-" + str(datetime.datetime.now().timestamp()) + result

    # def post(self, request, format=None):
    #     user = self.request.user

    #     try:
    #         # Find the unpaid order for the user
    #         order = Order.objects.get(user=user, ordered=False)

    #         # Generate transaction reference
    #         tx_ref = self.generate_tx_ref()
            
    #         # Here, you can add any other logic you need for initiating payment

    #         return Response({
    #             "tx_ref": tx_ref,
    #             "order_id": order.id,
    #             "total": order.get_total()
    #         }, status=status.HTTP_200_OK)

    #     except Order.DoesNotExist:
    #         return Response({"message": "No unpaid order found for this user"}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            self.paystack_secret_key = os.environ.get('PAYSTACK_SECRET_KEY')
            self.allowed_ips = ['52.31.139.75', '52.49.173.169', '52.214.14.220']

            payload = json.loads(request.body.decode('utf-8'))
            event = payload.get('event')
            data = payload.get('data', {})

            # Validate the paystack webhook signature
            byte_data = json.dumps(payload, sort_keys=True).encode('utf-8')
            calculated_hash = self.calculate_signature(byte_data)
            provided_hash = request.headers.get('X-Paystack-Signature')

            if calculated_hash != provided_hash:
                client_ip = request.META.get('REMOTE_ADDR', '')

                if client_ip not in self.allowed_ips:
                    return JsonResponse({'status': 'error', 'message': 'Access Denied: Your IP Address is not allowed'})
                    
                if event == 'charge.success':
                    fulfill_order(data)
                    return JsonResponse({'status': 'Transaction success'})
                elif event == "transfer.failed":
                    email_customer_about_failed_payment(data)
                    return JsonResponse({'status': 'Transaction Failed'})
            else:
                # This means the request is not from paystack
                return JsonResponse({'status': 'error', 'message': 'Invalid signature provided. Kindly provide the right payment validators'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid body data. Must be of type Json'})
        except Exception as e:
            # Handle exceptions appropriately
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def calculate_signature(self, data):
        # This assumes you have self.paystack_secret_key defined in your class
        hashed_object = hmac.new(self.paystack_secret_key.encode('utf-8'), data, hashlib.sha512)
        return hashed_object.hexdigest()
    

def fulfill_order(data):
    # data = {
    #         "id": 302961,
    #         "domain": "live",
    #         "status": "success",
    #         "reference": "qTPrJoy9Bx",
    #         "amount": 10000,
    #         "message": null,
    #         "gateway_response": "Approved by Financial Institution",
    #         "paid_at": "2016-09-30T21:10:19.000Z",
    #         "created_at": "2016-09-30T21:09:56.000Z",
    #         "channel": "card",
    #         "currency": "NGN",
    #         "ip_address": "41.242.49.37",
    #         "metadata": 0,
    #         "log": {
    #             "time_spent": 16,
    #             "attempts": 1,
    #             "authentication": "pin",
    #             "errors": 0,
    #             "success": false,
    #             "mobile": false,
    #             "input": [],
    #             "channel": null,
    #             "history": [
    #                 {
    #                     "type": "input",
    #                     "message": "Filled these fields: card number, card expiry, card cvv",
    #                     "time": 15
    #                 },
    #                 {
    #                     "type": "action",
    #                     "message": "Attempted to pay",
    #                     "time": 15
    #                 },
    #                 {
    #                     "type": "auth",
    #                     "message": "Authentication Required: pin",
    #                     "time": 16
    #                 }
    #             ]
    #         },
    #         "fees": null,
    #         "customer": {
    #             "id": 68324,
    #             "first_name": "BoJack",
    #             "last_name": "Horseman",
    #             "email": "bojack@horseman.com",
    #             "customer_code": "CUS_qo38as2hpsgk2r0",
    #             "phone": null,
    #             "metadata": null,
    #             "risk_action": "default"
    #         },
    #         "authorization": {
    #             "authorization_code": "AUTH_f5rnfq9p",
    #             "bin": "539999",
    #             "last4": "8877",
    #             "exp_month": "08",
    #             "exp_year": "2020",
    #             "card_type": "mastercard DEBIT",
    #             "bank": "Guaranty Trust Bank",
    #             "country_code": "NG",
    #             "brand": "mastercard",
    #             "account_name": "BoJack Horseman"
    #         },
    #         "plan": {}
    #     }
    
    print("Fulfilling order")
    customer_email = data["customer"].get("email")
    customer_email = "admin@admin.com"
    charge_id = data.get("id") 
    reference = data.get("reference") 
    amount = data.get("amount")
    receipt_url = data.get("receipt_url")
    created = data.get("created_at")
    paid = data.get("paid_at")
    status = data.get("status")
    metadata = data.get("metadata")
            
    user = User.objects.get(email=customer_email)
    
    payment = Payment(
        user=user, 
        charge_id=charge_id, 
        ref=reference,
        amount=amount, 
        date_created=created, 
        # receipt_url=receipt_url, 
        status=status, 
        paid_at=paid
    )
    payment.save()

    if metadata:
        order_id = metadata.get("order_id")
        order = Order.objects.get(id=order_id)
        order.ordered = True
        order.save()

        # update stocks from the Stock model
        for i, product in enumerate(order.products.all()):
            product_inventory_id = product.product.id
            product_stock = Stock.objects.get(id=product_inventory_id)
            
            current_units = product_stock.units - 1
            current_sold_units = product_stock.units_sold + 1

            new_stock_record = Stock.objects.get(product_inventory=product.product)
            new_stock_record.units=current_units
            new_stock_record.units_sold=current_sold_units
            new_stock_record.save()

    send_mail(
        subject="Order Fulfilled",
        message=f"Thank you for your purchase. Your purchased items are on their way to be delivered to you. Here is a receipt of payment",  # {receipt_url}",
        recipient_list=[customer_email],
        from_email=settings.DEFAULT_FROM_EMAIL,
    )

    return "Successfully charged user"


def create_order(session):
    print("Creating order")
    # email can be gotten from the database
    customer_email = session["receipt_email"]
    order_id = session["metadata"]["order_id"]

    order = Order.objects.get(id=order_id)
    product_list = []
    for i, product in enumerate(order.products.all()):
        product_list.append(product.product.product.name)

    products_names = " ".join(product_list)

    send_mail(
        subject="Order Created",
        message=f"Thank you for your purchase. Here is the products you ordered: \n\n{products_names} \n\nPlease wait as we process your order.",
        recipient_list=[customer_email],
        from_email=settings.DEFAULT_FROM_EMAIL,
    )


def email_customer_about_failed_payment(data):
    # TODO: fill me in
    print("Emailing customer")

    customer_email = data["recipient"]["email"]

    send_mail(
        subject="Purchase Failed",
        message=f"We apologise but your purchase was unsuccessful",
        recipient_list=[customer_email],
        from_email=settings.DEFAULT_FROM_EMAIL,
    )
