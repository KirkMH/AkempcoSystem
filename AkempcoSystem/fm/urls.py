from django.urls import path
from . import views


urlpatterns = [
    path('uom', views.UomListView.as_view(), name='uom_list'),
    path('uom/new/', views.UomCreateView.as_view(), name='new_uom'),
    path('uom/<int:pk>/edit/', views.UomUpdateView.as_view(), name='edit_uom'),

    path('category', views.CategoryListView.as_view(), name='category_list'),
    path('category/new/', views.CategoryCreateView.as_view(), name='new_category'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='edit_category'),

    path('supplier', views.SupplierListView.as_view(), name='supplier_list'),
    path('supplier/new/', views.SupplierCreateView.as_view(), name='new_supplier'),
    path('supplier/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='edit_supplier'),
    path('supplier/<int:pk>/detail/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    
    path('product', views.ProductListView.as_view(), name='product_list'),
    path('product/new/', views.ProductCreateView.as_view(), name='new_product'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='edit_product'),
    path('product/<int:pk>/detail/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/new/barcoding', views.generate_barcode_number, name='generate_barcode_number'),
]