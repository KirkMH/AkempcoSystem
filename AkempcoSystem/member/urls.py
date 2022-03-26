from django.urls import path
from . import views

urlpatterns = [
    path('creditor', views.creditor_list, name='cred_list'),
    path('creditor/dt', views.CreditorDTListView.as_view(), name='cred_dtlist'),
    path('creditor/new/', views.CreditorCreateView.as_view(), name='new_cred'),
    path('creditor/<int:pk>/edit/', views.CreditorUpdateView.as_view(), name='edit_cred'),

    path('', views.dashboard_member_view, name='dashboard_member'),
    path('history/transactions', views.transaction_history, name='transaction_history'),
    path('history/transactions/<int:pk>/open', views.open_transaction, name='open_transaction'),

    path('payment', views.PayableListView.as_view(), name='payable_list'),
    path('payment/<int:pk>/new', views.PaymentCreateView.as_view(), name='new_payment'),
]