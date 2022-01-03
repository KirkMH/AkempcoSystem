from django.urls import path
from . import views


urlpatterns = [
    path('history', views.ProductListView.as_view(), name='product_list_history'),
    path('history/<int:pk>/product', views.ProductDetailView.as_view(), name='product_history'),
]