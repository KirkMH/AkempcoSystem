from django.urls import path
from . import views

urlpatterns = [
    path('review', views.product_pricing_list, name='price_review'),
    path('review/dt', views.ProductPricingDTListView.as_view(), name='price_review_dt'),
    path('all', views.all_product_pricing_list, name='price_all'),
    path('all/dt', views.AllProductPricingDTListView.as_view(), name='price_all_dt'),
    path('product/<int:pk>/entry', views.ProductPricingCreateView.as_view(), name='pricing_form'),
    path('product/<int:pk>/detail', views.PricingDetailListView.as_view(), name='product_pricing_detail'),
]