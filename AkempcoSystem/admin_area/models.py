from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User


def get_vatable_percentage():
    store = Store.objects.all()
    if store:
        store = store.first()
        if is_store_vatable() and store.vat_percent:
            return store.vat_percent
    return 0

def is_store_vatable():
    store = Store.objects.all()
    if store:
        store = store.first()
        return store.vatable
    else:
        return False
        

# Feature is used to load in the side menu under the specified group
class Feature:
    FM_UOM = 1
    FM_CATEGORY = 2
    FM_SUPPLIER = 3
    FM_PRODUCT = 4
    TR_PURCHASES = 5
    TR_PRICING = 6
    TR_STOCKS = 7
    TR_RV = 8
    TR_BO = 12
    TR_POS = 13
    RP_PRODHIST = 9
    FM_CREDITOR = 10
    MEMBER_TRANS = 11

    LIST = (
        (FM_UOM, 'File Maintenance - Unit of Measure'),
        (FM_CATEGORY, 'File Maintenance - Category'),
        (FM_SUPPLIER, 'File Maintenance - Supplier'),
        (FM_PRODUCT, 'File Maintenance - Product'),
        (FM_CREDITOR, 'File Maintenance - Creditors'),
        (TR_PURCHASES, 'Transaction - Purchases'),
        (TR_PRICING, 'Transaction - Price Management'),
        (TR_STOCKS, 'Transaction - Stock Management'),
        (TR_RV, 'Transaction - Requisition Voucher'),
        (TR_BO, 'Transaction - Bad Orders'),
        (TR_POS, 'Transaction - Point-of-Sale'),
        (RP_PRODHIST, 'Reports - Product History'),
        (MEMBER_TRANS, 'Members - Transactions'),
    )


class FeatureList(models.Model):
    pass
    

# UserType is used to clasify users
class UserType:
    CREDITOR = 'Member/Creditor'
    WH_STAFF = 'Warehouse Staff'
    SALES = 'Sales Personnel'
    STOREKEEPER = 'Storekeeper'
    PURCHASER = 'Purchaser'
    OIC = 'Officer-In-Charge'
    AUDIT = 'Audit Committee'
    GM = 'General Manager'
    
    LIST = (
        (CREDITOR, 'Member/Creditor'),
        (WH_STAFF, 'Warehouse Staff'),
        (SALES, 'Sales Personnel'),
        (STOREKEEPER, 'Storekeeper'),
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
        default=None
    )
    linked_creditor_acct = models.ForeignKey(
        "sales.Creditor",
        verbose_name=_("If Member/Creditor, link account to"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )
    features = MultiSelectField(
        choices=Feature.LIST,
        max_length=50
    )
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

    @property
    def last_login(self):
        log = UserLog.objects.filter(user=self.user, action_taken='logged in').latest('timestamp')
        if log:
            return log.timestamp
        else:
            return None

    def __str__(self):
        return self.user.get_full_name()

    def get_permissions(self):
        list = []
        for f in self.features:
            list.append(int(f))
        return list


# Stores user log-in and log-out
class UserLog(models.Model):
    username = models.CharField(
        _("Username"), 
        max_length=100
    )
    user = models.ForeignKey(
        User,
        related_name='userlog',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )
    # logged in, logged out, failed login
    action_taken = models.CharField(
        _("Action taken"),
        max_length=100
    )
    timestamp = models.DateTimeField(
        _("Timestamp"), 
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.username} {self.action_taken} on {self.timestamp}"
    


class Store(models.Model):
    name = models.CharField(
        _("Store Name"), 
        max_length=100
    )
    address = models.CharField(
        _("Address"), 
        max_length=250
    )
    registration_number = models.CharField(
        _("Registration Number"),
        max_length=50,
        help_text=_("Please include the registration type."),
        null=True,
        blank=True
    )
    contact_numbers = models.CharField(
        _("Contact Numbers"), 
        max_length=100,
        help_text=_("Please indicate the type. Separate different contact numbers by comma. E.g., Telephone number: 111-2222"),
        null=True,
        blank=True
    )
    email = models.EmailField(
        _("Email Address"), 
        max_length=100,
        null=True,
        blank=True
    )
    # VAT details -- to date, AKEMPCO is VAT exempt
    vatable = models.BooleanField(
        _("Is the store VATable?"),
        default=False
    )
    vat_percent = models.PositiveSmallIntegerField(
        _("VAT Percentage"),
        null=True,
        blank=True,
        default=None
    )
    # markup details
    point_of_reference = models.DecimalField(
        _("Point of Reference"), 
        max_digits=5, 
        decimal_places=2
    )
    retail_markup_below = models.DecimalField(
        _("Retail Markup Below Point of Reference"), 
        max_digits=5, 
        decimal_places=2
    )
    retail_markup = models.DecimalField(
        _("Retail Markup From Point of Reference"), 
        max_digits=5, 
        decimal_places=2
    )
    wholesale_markup = models.DecimalField(
        _("Wholesale Markup"), 
        max_digits=5, 
        decimal_places=2
    )
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if Store.objects.count() == 1:
            raise ValidationError("You can only have one store record.")
        super().save(*args, **kwargs)