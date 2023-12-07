from django.urls import path

from order_management import views

inventory_url = [
    ###############################################################################
    path("inventory-dashboard/", views.DashboardView.as_view(), name="inventory_dashboard"),
    path("inventory-order-list/", views.InventoryOrderListView.as_view(), name="inventory_order_list"),
    path("inventory-product-list/", views.InventoryProductListView.as_view(), name="inventory_product_list"),
    path("inventory-product/<sku>/", views.InventoryProductView.as_view(), name="inventory_product"),
    path("inventory-product-edit/<sku>/", views.InventoryProductEditView.as_view(), name="inventory_product_edit"),
    # ###############################################################################
]

update_form_url = [
    # path("update/", views.UpdateView.as_view(), name="update"),
    # path("price-update/", views.PriceUpdateView.as_view(), name="price_update"),
    # path("product-create/", views.ProductCategoryCreateView.as_view(), name="product_create"),
    # path("product-attribute-create/", views.ProductAttributeCreateView.as_view(), name="product_attribute_create"),
    # path("update-done/", views.UpdateDoneView.as_view(), name="update_done"),
    # path("update-button/", views.UpdateButtonsView.as_view(), name="update_button"),
]

urlpatterns = inventory_url + update_form_url