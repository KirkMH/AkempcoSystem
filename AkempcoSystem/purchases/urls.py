from django.urls import path
from . import views


urlpatterns = [
    path('', views.PurchaseSupplierListView.as_view(), name='purchase_suppliers'),
    path('supplier/<int:pk>/po', views.PurchaseSupplierDetailView.as_view(), name='po_list'),
    path('supplier/<int:pk>/po/create', views.POCreateView.as_view(), name='po_create'),
    path('po/<int:pk>/edit', views.POUpdateView.as_view(), name='po_edit'),
    path('po/<int:pk>/delete', views.PODeleteView.as_view(), name='po_delete'),
    path('po/<int:pk>/products', views.PODetailView.as_view(), name='po_products'),
                                                                                                                                                                                                      
    path('po/<int:pk>/products/add', views.POProductCreateView.as_view(), name='product_add'),
    path('po/<int:pk>/products/<int:item_pk>/edit', views.POProductUpdateView.as_view(), name='product_edit'),
    path('po/<int:pk>/products/<int:item_pk>/delete', views.POProductDeleteView.as_view(), name='product_delete'),
    path('po/<int:pk>/submit', views.submit_po, name='submit_po'),
    path('po/<int:pk>/approve', views.approve_po, name='approve_po'),
    path('po/<int:pk>/reject', views.reject_po, name='reject_po'),

    path('ajax/select_product', views.select_product, name='select_product'),
    path('ajax/load_data', views.load_data, name='load_data'),
]