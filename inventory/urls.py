from django.urls import path

from inventory import views

urlpatterns = [
    path('trending-categories/', views.TrendingCategoriesView.as_view(), name='trending_categories'),
    path('product-inventory-sales/', views.OnSaleProductInventoryView.as_view(), name='on_sale_products'),
    path('products/', views.AllProductListView.as_view(), name='all_products'),
    path('product/<str:sku>/', views.ProductDetailView.as_view(), name='product-detail'),

    # -------------------- FILTER APIs --------------------
    path('categories/', views.CategoryTreeView.as_view(), name='category-tree'),
    path('brands/', views.BrandListView.as_view(), name='brand_list'),

    # -------------------- SEARCH SUGGESTIONS APIs --------------------
    path('product-suggestions/', views.ProductSuggestionView.as_view(), name='product-suggestions'),

    # -------------------
    path('test/', views.Test.as_view(), name="test")
]