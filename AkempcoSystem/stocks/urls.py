from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('dt', views.StockDTListView.as_view(), name='stock_dtlist'),    
    path('rv', views.rv_list, name='rv_list'),
    path('rv/dt', views.RVDTListView.as_view(), name='rv_dtlist'),
    path('rv/new', views.create_new_rv, name='new_rv'),
    path('rv/<int:pk>/cancel', views.delete_rv, name='cancel_rv'),
    path('rv/<int:pk>/print', views.PrintRVDetailView.as_view(), name='print_rv'),
    path('rv/<int:pk>/submit', views.submit_rv, name='submit_rv'),
    path('rv/<int:pk>/approve', views.approve_rv, name='approve_rv'),
    path('rv/<int:pk>/reject', views.reject_rv, name='reject_rv'),
    path('rv/<int:pk>/release', views.release_rv, name='release_rv'),
    path('rv/<int:pk>/receive', views.receive_rv, name='receive_rv'),
    path('rv/<int:pk>/clone', views.clone_rv, name='clone_rv'),
    
    path('rv/<int:pk>/products', views.RVDetailView.as_view(), name='rv_products'),
    path('rv/<int:pk>/products/add', views.RVProductCreateView.as_view(), name='rv_products_add'),
    path('rv/products/<int:pk>/delete', views.delete_rv_product, name='delete_rv_product'),
    path('rv/products/<int:pk>/update', views.RVProductUpdateView.as_view(), name='update_rv_product'),

    path('stockadj', views.adjustment_list, name='adjustment_list'),
    path('stockadj/dt', views.StockAdjustmentDTListView.as_view(), name='adjustment_dtlist'),
    path('stockadj/new', views.StockAdjustmentCreateView.as_view(), name='adjustment_new'),
    path('stockadj/<int:pk>/view', views.StockAdjustmentDetailView.as_view(), name='adjustment_view'),
    path('stockadj/<int:pk>/approve', views.approve_adjustment, name='adjustment_approve'),
    path('stockadj/<int:pk>/cancel', views.cancel_adjustment, name='adjustment_cancel'),
]