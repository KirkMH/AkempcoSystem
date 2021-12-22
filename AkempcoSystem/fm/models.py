from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# will be used for the status of different models
ACTIVE = 'ACTIVE'
CANCELLED = 'CANCELLED'
STATUS = [
    (ACTIVE, _('Active')),
    (CANCELLED, _('Cancelled'))
]


# UnitOfMeasure model
class UnitOfMeasure(models.Model):
    uom_description = models.CharField(
        _("Unit of measure"), 
        max_length=50, 
        help_text='Use singular form.',
        null=False
    )
    status = models.CharField(
        _("Status"), 
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )

    def __str__(self):
        return self.uom_description

    class Meta:
        ordering = ['uom_description']



# Category model
class Category(models.Model):
    category_description = models.CharField(
        _("Category description"), 
        max_length=50, 
        help_text='Use singular form.',
        null=False
    )
    status = models.CharField(
        _("Status"), 
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )

    def __str__(self):
        return self.category_description

    class Meta:
        ordering = ['category_description']


# Supplier model
class Supplier(models.Model):
    # for tax classification
    TAXABLE = 'Taxable'
    NONTAX = 'Non-Taxable'
    TAXEXEMPT = 'Tax Exempt'
    TAX_CLASSIFICATION = [
        (TAXABLE, _('Taxable')),
        (NONTAX, _('Non-Taxable')),
        (TAXEXEMPT, _('Tax Exempt'))
    ]

    supplier_name = models.CharField(
        _("Supplier Name"), 
        max_length=50
    )
    address = models.CharField(
        _("Address"), 
        max_length=250
    )
    contact_person = models.CharField(
        _("Contact Person"), 
        max_length=50
    )
    contact_info = models.CharField(
        _("Contact Information"), 
        max_length=50,
        null=True,
        blank=True
    )
    email = models.EmailField(
        _("Email"), 
        max_length=100,
        null=True,
        blank=True
    )
    tax_class = models.CharField(
        _("Tax Classification"), 
        max_length=50, 
        choices=TAX_CLASSIFICATION,
        default=None,
        null=True,
        blank=True
    )
    tin = models.CharField(
        _("Tax Identification Number"), 
        max_length=20,
        null=True,
        blank=True,
        default=None
    )
    less_vat = models.BooleanField(
        _("Supplier deducts VAT from total"), 
        default=False
    )
    notes = models.TextField(
        _("Notes"),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        _("Created at"), 
        auto_now_add=True
    )
    activated_at = models.DateTimeField(
        _("Activated at"),
        null=True
    )
    last_updated_at = models.DateTimeField(
        _("Last updated at"), 
        auto_now=True,
        null=True
    )
    cancelled_at = models.DateTimeField(
        _("Cancelled at"),
        null=True,
        default=None
    )
    status = models.CharField(
        _("Status"), 
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )

    def __str__(self):
        return self.supplier_name

    class Meta:
        ordering = ['supplier_name']
