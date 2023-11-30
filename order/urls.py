from django.urls import path

from order import views

urlpatterns = [
    path('add-to-cart/<sku>/<int:quantity>/', views.AddToCartAPIView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<sku>/', views.RemoveFromCartAPIView.as_view(), name='remove_from_cart'),
    path('remove-single-from-cart/<sku>/', views.RemoveSingleFromCartAPIView.as_view(), name='remove_single_from_cart'),

    path('order-summary/', views.OrderSummaryAPIView.as_view(), name='order_summary'),
    path('apply-coupon/<int:order_id>/<str:coupon_code>/', views.ApplyCouponAPIView.as_view(), name='apply_coupon'),
]