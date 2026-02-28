from django.contrib import admin
from .models import (
    ProductSalesReport, ProductSalesReportItem,
    InventoryCountReport, InventoryCountItem
)


class ProductSalesReportItemInline(admin.TabularInline):
    model = ProductSalesReportItem
    extra = 0
    readonly_fields = ('product', 'number_of_sold_items', 'total_sales', 'total_cogs')


class ProductSalesReportAdmin(admin.ModelAdmin):
    list_display = ('pk', 'generated_by', 'created_at')
    inlines = [ProductSalesReportItemInline]


class InventoryCountItemInline(admin.TabularInline):
    model = InventoryCountItem
    extra = 0
    readonly_fields = ('product', 'location', 'cycle', 'physical_count', 'expected_count', 'variance')


class InventoryCountReportAdmin(admin.ModelAdmin):
    list_display = ('pk', 'inventory_date', 'generated_by', 'warehouse_count_status',
                    'store_count_status', 'overall_status', 'created_at')
    list_filter = ('overall_status', 'inventory_date')
    inlines = [InventoryCountItemInline]


admin.site.register(ProductSalesReport, ProductSalesReportAdmin)
admin.site.register(InventoryCountReport, InventoryCountReportAdmin)
