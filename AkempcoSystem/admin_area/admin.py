from django import forms
from django.forms import inlineformset_factory
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from .models import UserDetail, Store
from purchases.models import PurchaseOrder, PO_Product
from stocks.models import WarehouseStock, StoreStock, ProductHistory, StockAdjustment
from sales.models import *
from member.models import Creditor, CreditorPayment
from fm.models import *


admin.site.site_header = 'AKEMPCO System Administrator'
admin.site.site_title  =  'System Admin Area'
admin.site.index_title  =  'AKEMPCO'

# Define an inline admin descriptor for UserDetail model
# which acts a bit like a singleton
class UserDetailAdminForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        exclude = ['user']
        widgets = {'features': forms.SelectMultiple()}

    # radio_fields = {"features": admin.VERTICAL}
UserDetailFormSet = inlineformset_factory(User, UserDetail, form=UserDetailAdminForm)

class UserDetailInline(admin.StackedInline):
    model = UserDetail
    formset = UserDetailFormSet
    can_delete = False
    verbose_name = _('Other Detail')


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'last_login', 'is_active')
    inlines = (UserDetailInline, )
    
    fieldsets = (
        (None, 
            {'fields': ('username', 'password')}),
        (_('Personal information'), 
            {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), 
            {'fields': ('is_active', 'is_staff')}),
        (_('Important dates'), 
            {'fields': ('last_login', 'date_joined')}),
    )

    def get_form(self, request, obj=None, **kwargs):
         self.exclude = ("user_permissions", "user_groups")
         ## Dynamically overriding
         self.fieldsets[2][1]["fields"] = ('is_active', 'is_staff')
         form = super(UserAdmin, self).get_form(request, obj, **kwargs)
         return form

class StoreAdmin(admin.ModelAdmin):
     def has_delete_permission(self, request, obj=None):
        return False

class DiscountAdmin(admin.ModelAdmin):
     def has_delete_permission(self, request, obj=None):
        return False

# custom action for admin to perform stock adjustment
@admin.action(description='Perform selected requests')
def perform_requests(modeladmin, request, queryset):
    for req in queryset:
        req.perform(request.user)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Store, StoreAdmin)

admin.site.register(WarehouseStock)
admin.site.register(StoreStock)
admin.site.register(ProductHistory)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'quantity', 'location', 'reason', 'created_by', 'status')
    actions = [perform_requests]
admin.site.register(StockAdjustment, StockAdjustmentAdmin)

admin.site.register(PurchaseOrder)
admin.site.register(PO_Product)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Creditor)
admin.site.register(CreditorPayment)
admin.site.register(Sales)
class SalesItemAdmin(admin.ModelAdmin):
    list_display = ('sales', 'product', 'unit_price', 'quantity', 'is_wholesale', 'less_vat', 'less_discount', 'subtotal', 'total')
admin.site.register(SalesItem, SalesItemAdmin)
admin.site.register(SalesItemCogs)
admin.site.register(SalesInvoice)
admin.site.register(SalesVoid)
admin.site.register(SalesPayment)

admin.site.register(Product)


# remove Group
admin.site.unregister(Group)