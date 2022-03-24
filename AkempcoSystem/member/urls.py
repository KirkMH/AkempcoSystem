from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_member_view, name='dashboard_member'),
    path('history/transactions', views.transaction_history, name='transaction_history'),
    path('history/transactions/<int:pk>/open', views.open_transaction, name='open_transaction'),
]