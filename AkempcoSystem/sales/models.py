from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User
from fm.models import Product


class Creditor(models.Model):
    CREDITOR_TYPES = [
        ('Member', _('Member')),
        ('Group', _('Group Creditor'))
    ]

    creditor_type = models.CharField(
        _("Creditor Type"),
        max_length=10,
        choices=CREDITOR_TYPES
    )
    name = models.CharField(
        _("Name"), 
        max_length=100
    )
    address = models.CharField(
        _("Address"), 
        max_length=250
    )
    credit_limit = models.DecimalField(
        _("Credit Limit"), 
        max_digits=10, 
        decimal_places=2
    )
    active = models.BooleanField(
        _("Is active?"),
        default=True
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Discount(models.Model):
    DISCOUNT_TYPES = [
        ('peso', _('Peso')),
        ('percent', _('Percent'))
    ]

    name = models.CharField(
        _("Discount name"), 
        max_length=50
    )
    discount_type = models.CharField(
        _("Discount Type"), 
        max_length=10,
        choices=DISCOUNT_TYPES
    )
    vatable_only = models.BooleanField(
        _("Apply to Vatable amount only?"),
        default=False
    )
    value = models.DecimalField(
        _("Value"), 
        max_digits=5, 
        decimal_places=2
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Sales(models.Model):
    total = models.DecimalField(
        _("Total"), 
        max_digits=10, 
        decimal_places=2
    )
    vatable = models.DecimalField(
        _("Vatable Amount"), 
        max_digits=10, 
        decimal_places=2
    )
    vat = models.DecimalField(
        _("VAT Amount"), 
        max_digits=10, 
        decimal_places=2
    )
    zero_rated = models.DecimalField(
        _("Zero-rated Sales"), 
        max_digits=10, 
        decimal_places=2
    )
    vat_exempt = models.DecimalField(
        _("VAT-exempt Sales"), 
        max_digits=10, 
        decimal_places=2
    )
    discount = models.DecimalField(
        _("Discount"), 
        max_digits=10, 
        decimal_places=2
    )
    payable = models.DecimalField(
        _("Payable Amount"), 
        max_digits=10, 
        decimal_places=2
    )
    discount_type = models.ForeignKey(
        Discount, 
        verbose_name=_("Discount Type"), 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    customer = models.ForeignKey(
        Creditor, 
        verbose_name=_("Customer"), 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    transaction_datetime = models.DateTimeField(
        _("Transaction Date/Time"), 
        auto_now_add=True
    )
    last_reprint = models.DateTimeField(
        _("Last Reprint"), 
        null=True,
        blank=True,
        default=None
    )
    reprint_by = models.ForeignKey(
        User, 
        verbose_name=_("Reprinted by"), 
        related_name='reprinted_by',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    cancelled_on = models.DateTimeField(
        _("Cancelled on"), 
        null=True,
        blank=True,
        default=None
    )
    cancelled_by = models.ForeignKey(
        User, 
        verbose_name=_("Cancelled by"), 
        related_name='cancelled_by',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    
    def __str__(self):
        return str(self.pk) + ": PhP " + str(self.payable)

    class Meta:
        ordering = ['-pk']


class SalesItem(models.Model):
    sales = models.ForeignKey(
        Sales, 
        verbose_name=_("Sales"), 
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product, 
        verbose_name=_("Product"), 
        on_delete=models.CASCADE,
    )
    unit_price = models.DecimalField(
        _("Unit Price"), 
        max_digits=10, 
        decimal_places=2
    )
    quantity = models.PositiveIntegerField(_("Quantity"))
    subtotal = models.DecimalField(
        _("Subtotal"), 
        max_digits=10, 
        decimal_places=2
    )
    discount = models.DecimalField(
        _("Discount"), 
        max_digits=10, 
        decimal_places=2
    )
    total = models.DecimalField(
        _("Total"), 
        max_digits=10, 
        decimal_places=2
    )
    supplier_price = models.DecimalField(
        _("Supplier Price"), 
        max_digits=10, 
        decimal_places=2
    )
    is_wholesale = models.BooleanField(
        _("Is wholesale?"),
        default=False
    )

    def __str__(self):
        return self.product.full_description + ": " + str(self.quantity)

    class Meta:
        ordering = ['product']