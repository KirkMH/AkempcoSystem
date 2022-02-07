from django import forms
from django.forms import inlineformset_factory
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from .models import UserDetail, Store
from purchases.models import PurchaseOrder
from stocks.models import WarehouseStock, StoreStock
from sales.models import Discount, Creditor, Sales, SalesPayment


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

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(WarehouseStock)
admin.site.register(StoreStock)
admin.site.register(PurchaseOrder)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Creditor)
admin.site.register(Sales)
admin.site.register(SalesPayment)

# remove Group
admin.site.unregister(Group)