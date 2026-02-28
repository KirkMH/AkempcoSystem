from django import forms
from django.forms import inlineformset_factory
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from .models import UserDetail, UserLog, Store
from purchases.models import PurchaseOrder, PO_Product
from stocks.models import WarehouseStock, StoreStock, ProductHistory, StockAdjustment, RequisitionVoucher, RV_Product
from sales.models import *
from member.models import Creditor, CreditorPayment
from fm.models import *
from entryadjustment.models import *


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
            {'fields': ('is_active', 'is_superuser')}),
        (_('Important dates'), 
            {'fields': ('last_login', 'date_joined')}),
    )

    def get_form(self, request, obj=None, **kwargs):
         self.exclude = ("user_permissions", "user_groups")
         ## Dynamically overriding
         self.fieldsets[2][1]["fields"] = ('is_active', 'is_superuser')
         form = super(UserAdmin, self).get_form(request, obj, **kwargs)
         return form

class StoreAdmin(admin.ModelAdmin):
     def has_delete_permission(self, request, obj=None):
        return False

class DiscountAdmin(admin.ModelAdmin):
     def has_delete_permission(self, request, obj=None):
        return False


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Store, StoreAdmin)

# ── Warehouse / Store Stocks ─────────────────────────────────────────────────
admin.site.register(WarehouseStock)
admin.site.register(StoreStock)
admin.site.register(ProductHistory)

# ── Requisition Voucher (parent) → RV_Product (child) ───────────────────────
class RVProductInline(admin.TabularInline):
    model = RV_Product
    extra = 0

class RequisitionVoucherAdmin(admin.ModelAdmin):
    list_display = ('pk', 'status', 'item_count', 'requested_by', 'requested_at')
    inlines = [RVProductInline]

admin.site.register(RequisitionVoucher, RequisitionVoucherAdmin)

# ── Stock Adjustment ─────────────────────────────────────────────────────────
@admin.action(description='Perform selected requests')
def perform_requests(modeladmin, request, queryset):
    for req in queryset:
        req.perform(request.user)

class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'quantity', 'location', 'reason', 'created_by', 'status')
    actions = [perform_requests]

admin.site.register(StockAdjustment, StockAdjustmentAdmin)

# ── Entry Adjustment ─────────────────────────────────────────────────────────
# @admin.action(description='Perform selected requests')
# def perform_entry_adj_requests(modeladmin, request, queryset):
#     for req in queryset:
#         req.perform(request.user)

# class EntryAdjustmentAdmin(admin.ModelAdmin):
#     list_display = ('requested_at', 'transaction_type', 'reference_num', 'adjustment_detail', 'reason', 'requested_by', 'status')
#     actions = [perform_entry_adj_requests]

# admin.site.register(EntryAdjustment, EntryAdjustmentAdmin)

# ── Purchase Order (parent) → PO_Product (child) ─────────────────────────────
class POProductInline(admin.TabularInline):
    model = PO_Product
    extra = 0
    readonly_fields = ('undelivered_qty', 'po_subtotal', 'received_subtotal', 'has_received')

class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'supplier', 'category', 'po_date', 'status', 'item_count', 'total_po_amount', 'prepared_by')
    list_filter = ('status', 'is_open')
    search_fields = ('supplier__supplier_name',)
    inlines = [POProductInline]

admin.site.register(PurchaseOrder, PurchaseOrderAdmin)

# ── Discount ─────────────────────────────────────────────────────────────────
admin.site.register(Discount, DiscountAdmin)

# ── Creditor (parent) → CreditorPayment (child) ──────────────────────────────
class CreditorPaymentInline(admin.TabularInline):
    model = CreditorPayment
    extra = 0
    readonly_fields = ('date_posted',)

class CreditorAdmin(admin.ModelAdmin):
    list_display = ('name', 'creditor_type', 'id_number', 'credit_limit', 'payable', 'remaining_credit', 'active')
    list_filter = ('creditor_type', 'active')
    search_fields = ('name', 'id_number')
    inlines = [CreditorPaymentInline]

admin.site.register(Creditor, CreditorAdmin)

# ── Sales (parent) → SalesItem + SalesPayment (children) ─────────────────────
class SalesItemInline(admin.TabularInline):
    model = SalesItem
    extra = 0
    readonly_fields = ('subtotal', 'total', 'vatable', 'vat_amount', 'vat_exempt', 'zero_rated')

class SalesPaymentInline(admin.TabularInline):
    model = SalesPayment
    extra = 0

class SalesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'cashier', 'transaction_datetime', 'status', 'item_count', 'payable', 'customer')
    list_filter = ('status',)
    inlines = [SalesItemInline, SalesPaymentInline]

admin.site.register(Sales, SalesAdmin)
admin.site.register(SalesItemCogs)

# ── SalesInvoice (parent) → SalesVoid (child, one-to-one) ────────────────────
class SalesVoidInline(admin.StackedInline):
    model = SalesVoid
    extra = 0
    can_delete = False

class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sales', 'sales_datetime', 'is_cancelled', 'payment_modes')
    list_filter = ('is_cancelled',)
    inlines = [SalesVoidInline]

admin.site.register(SalesInvoice, SalesInvoiceAdmin)

# ── Product ───────────────────────────────────────────────────────────────────
admin.site.register(Product)

# ── User Log ──────────────────────────────────────────────────────────────────
admin.site.register(UserLog)

# ── X-Reading (parent) → TenderReport + DiscountReport (children) ────────────
class TenderReportInline(admin.TabularInline):
    model = TenderReport
    extra = 0

class DiscountReportInline(admin.TabularInline):
    model = DiscountReport
    extra = 0

class XReadingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created_by', 'created_at', 'total_sales', 'gross_sales', 'transaction_count', 'void_count')
    inlines = [TenderReportInline, DiscountReportInline]

admin.site.register(XReading, XReadingAdmin)

# ── Z-Reading (parent) → XReading (child, one-to-one) ────────────────────────
class ZReadingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'xreading', 'beginning_bal', 'ending_bal', 'transaction_count')

admin.site.register(ZReading, ZReadingAdmin)


# remove Group
admin.site.unregister(Group)