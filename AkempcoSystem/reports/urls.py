from django.urls import path
from . import views


urlpatterns = [
    path('history', views.product_list_history, name='product_list_history'),
    path('history/<int:pk>/product/warehouse',
         views.product_warehouse_history, name='product_history_w'),
    path('history/<int:pk>/product/warehouse/dt',
         views.ProductWarehouseDTView.as_view(), name='product_history_w_dt'),
    path('history/<int:pk>/product/store',
         views.product_store_history, name='product_history_s'),
    path('history/<int:pk>/product/store/dt',
         views.ProductStoreDTView.as_view(), name='product_history_s_dt'),

    path('critical', views.critical_products, name='product_list_critical'),
    path('critical/dt', views.CriticalStockDTListView.as_view(),
         name='critical_dtlist'),

    path('itr/', views.inventoryTurnoverRatio, name='itr_report'),
    path('itr/dt',
         views.InventoryTurnoverRatioDTView.as_view(), name='itr_dtlist'),

    path('sales', views.sales_report, name='sales_report'),
    path('sales/dt', views.GenerateSalesReport.as_view(),
         name='generate_sales_report'),
]
