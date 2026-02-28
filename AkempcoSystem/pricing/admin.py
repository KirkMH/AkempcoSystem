from django.contrib import admin
from .models import ProductPricing


class ProductPricingAdmin(admin.ModelAdmin):
    list_display = ('product', 'retail_price', 'wholesale_price', 'price_updated_on', 'price_tagged_by')
    search_fields = ('product__full_description',)
    list_filter = ('price_updated_on',)


admin.site.register(ProductPricing, ProductPricingAdmin)
