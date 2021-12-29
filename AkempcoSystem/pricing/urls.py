from django.urls import path
from . import views

urlpatterns = [
    path('review', views.ProductPricingListView.as_view(), name='price_review'),
    path('all', views.AllProductPricingListView.as_view(), name='price_all'),
]