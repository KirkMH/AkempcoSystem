from django.db import models
from django.utils.translation import gettext_lazy as _
import decimal

from django.contrib.auth.models import User
from fm.models import Product
from admin_area.models import get_vatable_percentage


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
        help_text="Is this member/creditor still active?",
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
    active = models.BooleanField(
        _("Is active?"),
        help_text="Is this discount type still active?",
        default=True
    )

    def __str__(self):
        unit = ' PhP' if self.discount_type == 'peso' else '%'
        return self.name + ': ' + str(self.value) + unit

    class Meta:
        ordering = ['name']


class Sales(models.Model):
    STATUS_LIST = [
        ('WIP', _('Work-in-Progress')),
        ('On-Hold', _('On-Hold')),
        ('Completed', _('Completed')),
        ('Cancelled', _('Cancelled')),
    ]

    discount = models.DecimalField(
        _("Discount"), 
        max_digits=10, 
        decimal_places=2,
        default=0
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
    status = models.CharField(
        _("Status"), 
        max_length=10,
        choices=STATUS_LIST,
        default='WIP'
    )
    
    def __str__(self):
        return str(self.pk) + ": PhP " + str(self.payable)

    # helper method to compute total of items
    def compute_total(self, items):
        total = 0.0
        if items:
            for item in items:
                total = total + item.total
        return total

    @property
    def total(self):
        items = SalesItem.objects.filter(sales=self)
        return self.compute_total(items)

    @property
    def vatable(self):
        items = SalesItem.objects.filter(sales=self, product__tax_type='V')
        # this is the total with VAT
        total = self.compute_total(items)
        # less the VAT
        vat_p = 1 + get_vatable_percentage()
        return total / vat_p
       
    @property
    def vat(self):
        items = SalesItem.objects.filter(sales=self, product__tax_type='V')
        # this is the total with VAT
        total = self.compute_total(items)
        # less the VAT
        vat_p = 1 + get_vatable_percentage()
        return total - total / vat_p

    @property
    def zero_rated(self):
        items = SalesItem.objects.filter(sales=self, product__tax_type='Z')
        total = self.compute_total(items)
        return total

    @property
    def vat_exempt(self):
        items = SalesItem.objects.filter(sales=self, product__tax_type='X')
        total = self.compute_total(items)
        return total

    @property
    def payable(self):
        return decimal.Decimal(self.total) - self.discount

    def get_next_si(self):
        si = SalesInvoice.objects.all()[:1]
        if si:
            return si.pk + 1
        else:
            return 1

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

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    class Meta:
        ordering = ['product']


class SalesInvoice(models.Model):
    sales = models.OneToOneField(
        Sales, 
        verbose_name=_("Sales Record"), 
        on_delete=models.CASCADE,
    )
    sales_datetime = models.DateTimeField(
        _("SI Date/Time"), 
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

    class Meta:
        ordering = ['-pk']