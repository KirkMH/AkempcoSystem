from django.urls import path
from . import views


urlpatterns = [
    path('', views.PurchaseSupplierListView.as_view(), name='purchase_suppliers'),
    path('supplier/<int:pk>/po_list', views.PurchaseSupplierDetailView.as_view(), name='po_list'),
]