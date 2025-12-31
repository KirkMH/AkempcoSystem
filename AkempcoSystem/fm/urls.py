from django.urls import path
from . import views


urlpatterns = [
    path('uom', views.uom_list, name='uom_list'),
    path('uom/dt', views.UomDTListView.as_view(), name='uom_dtlist'),
    path('uom/new/', views.UomCreateView.as_view(), name='new_uom'),
    path('uom/<int:pk>/edit/', views.UomUpdateView.as_view(), name='edit_uom'),

    path('discount', views.discount_list, name='discount_list'),
    path('discount/dt', views.DiscountDTListView.as_view(), name='discount_dtlist'),
    path('discount/new/', views.DiscountCreateView.as_view(), name='new_discount'),
    path('discount/<int:pk>/edit/', views.DiscountUpdateView.as_view(), name='edit_discount'),

    path('category', views.category_list, name='category_list'),
    path('category/dt', views.CategoryDTListView.as_view(), name='category_dtlist'),
    path('category/new/', views.CategoryCreateView.as_view(), name='new_category'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='edit_category'),

    path('supplier', views.supplier_list, name='supplier_list'),
    path('supplier/dt', views.SupplierDTListView.as_view(), name='supplier_dtlist'),
    path('supplier/new/', views.SupplierCreateView.as_view(), name='new_supplier'),
    path('supplier/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='edit_supplier'),
    path('supplier/<int:pk>/detail/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    
    path('product', views.product_list, name='product_list'),
    path('product/dt', views.ProductDTListView.as_view(), name='product_dtlist'),
    path('product/new/', views.ProductCreateView.as_view(), name='new_product'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='edit_product'),
    path('product/<int:pk>/detail/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/new/barcoding', views.generate_barcode_number, name='generate_barcode_number'),
]