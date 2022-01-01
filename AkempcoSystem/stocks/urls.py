from django.urls import path
from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='stock_list'),
    path('rv', views.RVListView.as_view(), name='rv_list'),
    path('rv/new', views.create_new_rv, name='new_rv'),
    path('rv/<int:pk>/cancel', views.delete_rv, name='cancel_rv'),
    path('rv/<int:pk>/print', views.PrintRVDetailView.as_view(), name='print_rv'),
    path('rv/<int:pk>/submit', views.submit_rv, name='submit_rv'),
    path('rv/<int:pk>/approve', views.approve_rv, name='approve_rv'),
    path('rv/<int:pk>/reject', views.reject_rv, name='reject_rv'),
    
    path('rv/<int:pk>/products', views.RVDetailView.as_view(), name='rv_products'),
    path('rv/<int:pk>/products/add', views.RVProductCreateView.as_view(), name='rv_products_add'),
    path('rv/products/<int:pk>/delete', views.delete_rv_product, name='delete_rv_product'),
    path('rv/products/<int:pk>/update', views.RVProductUpdateView.as_view(), name='update_rv_product'),
]