from django.urls import path
from . import views

urlpatterns = [
    path('review', views.ProductPricingListView.as_view(), name='price_review'),
    path('all', views.AllProductPricingListView.as_view(), name='price_all'),
    path('product/<int:pk>/entry', views.ProductPricingCreateView.as_view(), name='pricing_form'),
    path('product/<int:pk>/detail', views.PricingDetailListView.as_view(), name='product_pricing_detail'),
]