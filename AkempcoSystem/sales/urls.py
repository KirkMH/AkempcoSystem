from django.urls import path
from . import views

urlpatterns = [
    path('creditor', views.creditor_list, name='cred_list'),
    path('creditor/dt', views.CreditorDTListView.as_view(), name='cred_dtlist'),
    path('creditor/new/', views.CreditorCreateView.as_view(), name='new_cred'),
    path('creditor/<int:pk>/edit/', views.CreditorUpdateView.as_view(), name='edit_cred'),

    path('pos', views.pos_view, name='pos'),
    path('pos/<int:pk>/transaction', views.pos_view, name='load_pos'),
    path('pos/<int:pk>/add', views.add_to_cart, name='addToCart'),
    path('pos/<int:pk>/remove', views.remove_from_cart, name='removeFromCart'),
    path('pos/<int:pk>/checkout', views.PaymentDetailView.as_view(), name='checkout'),
    path('pos/<int:pk>/checkout/payment', views.SalesPaymentCreateView.as_view(), name='payment'),
    path('pos/<int:pk>/checkout/<int:payment_pk>/remove', views.remove_payment, name='removePayment'),
    path('pos/<int:pk>/checkout/complete', views.complete_checkout, name='completeCheckout'),
    path('pos/<int:pk>/invoice', views.sales_invoice, name='sales_invoice'),
    path('pos/<int:pk>/reset', views.reset_cart, name='reset_cart'),
    path('pos/<int:pk>/copy', views.copy_receipt, name='copy_receipt'),

    path('pos/<int:pk>/search/product', views.product_search, name='pos_product_search'),
    path('pos/<int:pk>/search/creditor', views.creditor_search, name='pos_creditor_search'),
    path('pos/<int:pk>/search/creditor/update', views.update_creditor, name='update_creditor'),
    path('pos/search/creditor/do', views.do_creditor_search, name='do_creditor_search'),

    path('pos/open', views.open_receipt, name='open_receipt'),
    path('pos/<int:pk>/invoice/<int:for_transaction>/open', views.sales_invoice, name='open_sales_invoice'),
    path('pos/<int:pk>/invoice/reprint', views.reprint_receipt, name='reprint_receipt'),
    path('pos/<int:pk>/invoice/cancel', views.cancel_receipt, name='cancel_receipt'),

    path('pos/<int:pk>/discount/apply', views.SalesDiscountUpdateView.as_view(), name='apply_discount'),
    path('pos/discount/validate', views.password_for_discount, name='validate_discount_pw'),

    path('pos/x_reading', views.x_reading, name='x_reading'),
    path('pos/z_reading', views.z_reading, name='z_reading'),
    path('pos/validate_gm_password', views.validate_gm_password, name='validate_gm_password'),
]