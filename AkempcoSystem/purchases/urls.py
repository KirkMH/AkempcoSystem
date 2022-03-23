from django.urls import path
from . import views


urlpatterns = [
    path('list', views.purchasesupplier_list, name='purchase_suppliers'),
    path('list/all/supplier', views.POSupplierListView.as_view(), name='purchase_suppliers_all'),
    path('list/approval', views.ApprovalListView.as_view(), name='po_approval'),
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
    path('po/<int:pk>/print', views.PurchaseOrderDetailView.as_view(), name='print_po'),
    path('po/<int:pk>/receiving/print', views.PODetailViewRR.as_view(), name='print_receiving'),
    path('po/<int:pk>/variance/print', views.PODetailViewVR.as_view(), name='print_variance'),

    path('po/<int:pk>/receive', views.PODetailViewReceiveStocks.as_view(), name='receive_stocks'),
    path('po/<int:pk>/receive/<int:item_pk>/update_receive_now', views.update_receive_now, name='update_receive_now'),
    path('po/<int:pk>/receive/update_unit_price', views.update_unit_price, name='update_unit_price'),
    path('po/<int:pk>/receive/update_ref_no', views.update_ref_no, name='update_ref_no'),
    path('po/<int:pk>/receive/update_price_review', views.update_price_review, name='update_price_review'),
    path('po/<int:pk>/receive/save', views.receive_stocks_save, name='receive_stocks_save'),

    path('po/<int:pk>/clone', views.clone_po, name='clone_po'),
    path('po/<int:pk>/undelivered', views.POUndeliveredDetailView.as_view(), name='view_undelivered'),
    path('po/<int:pk>/split_backorder', views.split_backorder, name='split_backorder'),
    path('po/<int:pk>/cancel_undelivered', views.cancel_undelivered, name='cancel_undelivered'),

    path('ajax/select_product', views.select_product, name='select_product'),
    path('ajax/load_data', views.load_data, name='load_data'),
]