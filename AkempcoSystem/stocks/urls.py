from django.urls import path
from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='stock_list'),
    path('rv', views.RVListView.as_view(), name='rv_list'),
]