from django.urls import path
from . import views


urlpatterns = [
    path('', views.PurchaseSupplierListView.as_view(), name='purchase_suppliers'),
    path('supplier/<int:pk>/po', views.PurchaseSupplierDetailView.as_view(), name='po_list'),
    path('supplier/<int:pk>/po/create', views.POCreateView.as_view(), name='po_create'),
    path('supplier/<int:pk>/po/<int:po_pk>/edit', views.POCreateView.as_view(), name='po_edit'),
    path('supplier/<int:pk>/po/<int:po_pk>/products', views.PODetailView.as_view(), name='po_products'),
]