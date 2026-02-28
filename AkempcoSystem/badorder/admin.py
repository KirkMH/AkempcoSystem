from django.contrib import admin
from .models import BadOrder, BadOrderItem


class BadOrderItemInline(admin.TabularInline):
    model = BadOrderItem
    extra = 0
    readonly_fields = ('total_cost',)


class BadOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'supplier', 'date_discovered', 'in_warehouse',
                    'number_of_items', 'grand_total', 'get_status', 'reported_by')
    list_filter = ('in_warehouse', 'process_step')
    search_fields = ('supplier__supplier_name',)
    inlines = [BadOrderItemInline]


admin.site.register(BadOrder, BadOrderAdmin)
