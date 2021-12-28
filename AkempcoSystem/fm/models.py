from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User
from admin_area.models import UserDetail
from purchases.models import PurchaseOrder, WarehouseStock, StoreStock

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
    oic = models.ForeignKey(
        UserDetail, 
        verbose_name=_("Officer-in-Charge"), 
        on_delete=models.RESTRICT,
        null=True
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

    def get_last_po(self):
        try:
            return PurchaseOrder.objects.filter(supplier=self).order_by('-pk')[:1].get()
        except:
            return None

    def get_number_of_open_po(self):
        try:
            return PurchaseOrder.objects.filter(supplier=self).filter(is_open=True, process_step__lt=6).count()
        except:
            return 0

    def get_po_count(self):
        try:
            return PurchaseOrder.objects.filter(supplier=self, process_step__lt=6).count()
        except:
            return 0

    def get_completion_rate(self):
        try:
            open_ctr = self.get_number_of_open_po()
            po_ctr = self.get_po_count()
            closed_ctr = po_ctr - open_ctr
            return closed_ctr / po_ctr
        except:
            return 0

    class Meta:
        ordering = ['supplier_name']


# Product model
class Product(models.Model):
    # for TaxType
    VAT = 'VAT'
    VATEX = 'VAT Exempt'
    ZERO = 'Zero-Rated'
    TAXTYPE = [
        (VAT, _("VAT")),
        (VATEX, _("VAT Exempt")),
        (ZERO, _("Zero Rated"))
    ]

    barcode = models.CharField(
        _("Barcode"), 
        max_length=50,
        unique=True,
    )
    full_description = models.CharField(
        _("Product description"), 
        max_length=250,
        unique=True
    )
    short_name = models.CharField(
        _("Short name"), 
        max_length=50,
        unique=True,
        help_text=_("This will appear in the receipt")
    )
    category = models.ForeignKey(
        Category, 
        verbose_name=_("Category"), 
        on_delete=models.RESTRICT
    )
    uom = models.ForeignKey(
        UnitOfMeasure, 
        verbose_name=_("Unit of Measurement"), 
        on_delete=models.RESTRICT
    )
    reorder_point = models.PositiveIntegerField(
        _("Reorder Point"),
        default=20,
        help_text=_("The level (quantity) when you will need to place an order so you won't run out of stock.")
    )
    ceiling_qty = models.PositiveIntegerField(
        _("Ceiling Quantity"),
        default=50,
        help_text=_("The maximum quantity you should keep in inventory in order to meet your demand and avoid overstocking.")
    )
    suggested_retail_price = models.DecimalField(
        _("Suggested Retail Price"), 
        max_digits=11, 
        decimal_places=2,
        default=0,
        null=True,
        blank=True
    )
    selling_price = models.DecimalField(
        _("Selling Price"), 
        max_digits=11, 
        decimal_places=2,
        null=True,
        blank=True
    )
    wholesale_price = models.DecimalField(
        _("Wholesale Price"), 
        max_digits=11, 
        decimal_places=2,
        null=True,
        blank=True
    )
    wholesale_qty = models.IntegerField(
        _("Wholesale Quantity"),
        default=0,
        help_text=_("Quantity to consider as wholesale")
    )
    tax_type = models.CharField(
        _("Tax Type"), 
        max_length=15,
        choices=TAXTYPE,
        default=VAT
    )
    is_consignment = models.BooleanField(
        _("Consigned product?"),
        help_text=_("Is this a consigned product?"),
        default=False
    )
    is_buyer_info_needed = models.BooleanField(
        _("Buyer's information needed?"),
        help_text=_("Do you need to get the buyer's information upon purchase?"),
        default=False
    )
    other_info = models.TextField(
        _("Other Information"),
        null=True,
        blank=True
    )
    for_price_review = models.BooleanField(
        _("For price review?"),
        default=False
    )
    created_at = models.DateTimeField(
        _("Created at"), 
        auto_now_add=True
    )
    price_updated_on = models.DateField(
        _("Price updated on"),
        null=True,
        default=None 
    )
    cancelled_at = models.DateTimeField(
        _("Cancelled at"),
        null=True,
        default=None 
    )
    suppliers = models.ManyToManyField(Supplier)
    status = models.CharField(
        _("Status"), 
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )
    price_review = models.BooleanField(
        _("For price review?"),
        default=False
    )

    def __str__(self):
        return self.full_description

    def is_consigned(self):
        return 'Yes' if self.is_consignment else 'No'

    def is_buyer_info_required(self):
        return 'Yes' if self.is_buyer_info_needed else 'No'

    def get_store_stock_count(self):
        return StoreStock.availableStocks.filter(product=self).aggregate(total=Sum('remaining_stocks'))['total']

    def get_warehouse_stock_count(self):
        return WarehouseStock.availableStocks.filter(product=self).aggregate(total=Sum('remaining_stocks'))['total']

    def get_total_stock_count(self):
        return self.get_store_stock_count() + self.get_warehouse_stock_count()

    class Meta:
        ordering = ['full_description']
    

# ProductPricing model, for price monitoring
class ProductPricing(models.Model):
    product = models.ForeignKey(
        Product, 
        verbose_name=_("Product"), 
        on_delete=models.CASCADE
    )
    selling_price = models.DecimalField(
        _("Selling Price"), 
        max_digits=11, 
        decimal_places=2,
        null=True,
        blank=True
    )
    wholesale_price = models.DecimalField(
        _("Wholesale Price"), 
        max_digits=11, 
        decimal_places=2,
        null=True,
        blank=True
    )
    price_updated_on = models.DateField(
        _("Price updated on"),
        null=True,
        default=None 
    )
    price_tagged_by = models.ForeignKey(
        User,
        verbose_name=_("Price tagged by"),
        on_delete=models.RESTRICT
    )