from django.urls import path
from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='stock_list'),
    path('rv', views.RVListView.as_view(), name='rv_list'),
    path('rv/new', views.create_new_rv, name='new_rv'),
    path('rv/<int:pk>/products', views.RVDetailView.as_view(), name='rv_products'),
    path('rv/<int:pk>/products/add', views.RVProductCreateView.as_view(), name='rv_products_add'),
]