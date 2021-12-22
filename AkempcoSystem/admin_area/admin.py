from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import UserDetail
from django.utils.translation import gettext_lazy as _


admin.site.site_header = 'AKEMPCO System Admin'
admin.site.site_title  =  'AKEMPCO System Admin Area'
admin.site.index_title  =  'AKEMPCO System Admin'


# Define an inline admin descriptor for UserDetail model
# which acts a bit like a singleton
class UserDetailInline(admin.StackedInline):
    model = UserDetail
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

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# remove Group
admin.site.unregister(Group)