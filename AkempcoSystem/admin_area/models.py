from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User

# Feature is used to load in the side menu under the specified group
class Feature:
    FM_UOM = 1
    FM_CATEGORY = 2
    FM_SUPPLIER = 3
    FM_PRODUCT = 4
    TR_PURCHASES = 5
    TR_PRICING = 6
    TR_RV = 7

    LIST = (
        (FM_UOM, 'File Maintenance - Unit of Measure'),
        (FM_CATEGORY, 'File Maintenance - Category'),
        (FM_SUPPLIER, 'File Maintenance - Supplier'),
        (FM_PRODUCT, 'File Maintenance - Product'),
        (TR_PURCHASES, 'Transaction - Purchases'),
        (TR_PRICING, 'Transaction - Price Management'),
        (TR_RV, 'Transaction - Requisition Voucher'),
    )
    

# UserType is used to clasify users
class UserType:
    PURCHASER = 'Purchaser'
    OIC = 'Officer-In-Charge'
    AUDIT = 'Audit Committee'
    GM = 'General Manager'
    
    LIST = (
        (PURCHASER, 'Purchaser'),
        (OIC, 'Officer-In-Charge'),
        (AUDIT, 'Audit Committee'),
        (GM, 'General Manager')
    )


# UserDetail is an extension of the built-in User model
class UserDetail(models.Model):
    user = models.OneToOneField(
        User,
        related_name='userdetail',
        on_delete=models.CASCADE
    )
    contact_no = models.CharField(
        _("Contact number"), 
        max_length=50,
        blank=True,
        null=True
    )
    userType = models.CharField(
        choices=UserType.LIST,
        max_length=20
    )
    oic_for = models.ForeignKey(
        "fm.Category",
        verbose_name=_("If OIC, select category"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=True
    )
    features = MultiSelectField(choices=Feature.LIST)
    activated_at = models.DateTimeField(
        _("Activated at"),
        null=True,
        blank=True,
        default=None
    )
    cancelled_at = models.DateTimeField(
        _("Cancelled at"),
        null=True,
        blank=True,
        default=None
    )
    notes = models.TextField(
        _("Notes"),
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.get_full_name()

    def get_permissions(self):
        list = []
        for f in self.features:
            list.append(int(f))
        return list