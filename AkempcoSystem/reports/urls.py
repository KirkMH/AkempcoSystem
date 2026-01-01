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

    path('sales/daily', views.daily_sales_report, name='daily_sales_report'),
    path('sales/daily/dt', views.GenerateDailySalesReport.as_view(),
         name='generate_daily_sales_report'),
    path('sales/product', views.product_sales_report, name='product_sales_report'),
    path('sales/product/dt', views.GenerateProductSalesReport.as_view(),
         name='generate_product_sales_report'),
]
