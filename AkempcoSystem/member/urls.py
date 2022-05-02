from django.urls import path
from . import views

urlpatterns = [
    path('creditor', views.creditor_list, name='cred_list'),
    path('creditor/dt', views.CreditorDTListView.as_view(), name='cred_dtlist'),
    path('creditor/new/', views.CreditorCreateView.as_view(), name='new_cred'),
    path('creditor/<int:pk>/edit/', views.CreditorUpdateView.as_view(), name='edit_cred'),

    path('', views.dashboard_member_view, name='dashboard_member'),
    path('transactions/history', views.transaction_history, name='transaction_history'),
    path('transactions/history/dt', views.TransactionHistoryDTListView.as_view(), name='transaction_history_dt'),
    path('transactions/history/<int:pk>/open', views.open_transaction, name='open_transaction'),

    path('payment', views.payable_listview, name='payable_list'),
    path('payment/<int:pk>/new', views.PaymentCreateView.as_view(), name='new_payment'),
    path('payment/history', views.payment_history, name='payment_history'),
    path('payment/history/dt', views.PaymentHistoryDTListView.as_view(), name='payment_history_dt'),
    path('payment/download', views.download_csv, name='download_csv'),
    path('payment/upload', views.upload_csv, name='upload_csv'),
]