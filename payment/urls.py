from django.urls import path

from payment import views

urlpatterns = [
    path('initiate-payment/', views.InitiatePayment.as_view(), name='initiate_payment'),
]