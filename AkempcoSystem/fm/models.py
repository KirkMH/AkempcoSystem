from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Min, Max, Sum, F, Q
import math

from django.contrib.auth.models import User
from admin_area.models import UserDetail, Store
from purchases.models import PurchaseOrder, PO_Product
from stocks.models import WarehouseStock, StoreStock, ProductHistory

# will be used for the status of different models
ACTIVE = 'ACTIVE'
CANCELLED = 'CANCELLED'
STATUS = [
    (ACTIVE, _('Active')),
    (CANCELLED, _('Cancelled'))
]

# used to round the value up to the nearest 5 cents, for pricing
def round_up(x):
    return math.ceil(x / 0.05) * 0.05

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


# class ProductManager(models.Manager):
#     def critical_level(self):
#         s_stocks = StoreStock.availableStocks.filter(product=self.product).aggregate(total=Sum('remaining_stocks'))['total']
#         if s_stocks is None: s_stocks = 0

#         w_stocks = WarehouseStock.availableStocks.filter(product=self.product).aggregate(total=Sum('remaining_stocks'))['total']
#         if w_stocks is None: w_stocks = 0

#         total_stocks = s_stocks + w_stocks
#         return self.filter(reorder_point__gte=total_stocks)


# Product model
class Product(models.Model):
    # for TaxType
    VAT = 'V'
    VATEX = 'E'
    ZERO = 'Z'
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
        max_length=1,
        choices=TAXTYPE,
        default=VAT
    )
    for_discount = models.BooleanField(
        _("Basic necessity or prime commodity?"),
        help_text=_("Is this a basic necessity or prime commodity? SC and PWD discounts will be applied."),
        default=False
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
    # objects = models.Manager()
    # misc_qs = ProductManager()

    @property
    def tax_type_description(self):
        for tt in self.TAXTYPE:
            if tt[0] == self.tax_type:
                return tt[1]
        return ''

    def __str__(self):
        return self.full_description

    def is_consigned(self):
        return 'Yes' if self.is_consignment else 'No'

    def is_buyer_info_required(self):
        return 'Yes' if self.is_buyer_info_needed else 'No'

    def get_store_stock_count(self):
        stocks = StoreStock.availableStocks.filter(product=self).aggregate(total=Sum('remaining_stocks'))['total']
        if stocks is None: stocks = 0
        return stocks

    def get_warehouse_stock_count(self):
        stocks = WarehouseStock.availableStocks.filter(product=self).aggregate(total=Sum('remaining_stocks'))['total']
        if stocks is None: stocks = 0
        return stocks

    def get_total_stock_count(self):
        store = self.get_store_stock_count()
        warehouse = self.get_warehouse_stock_count()
        return store + warehouse

    def get_on_order_qty(self):
        qty = PO_Product.objects.filter(
                Q(product=self) &
                Q(purchase_order__is_open=True) &
                Q(purchase_order__process_step__gt=1) &
                Q(purchase_order__process_step__lt=6)
            ).aggregate(on_order=Sum('ordered_quantity'))['on_order']
        return qty if qty else 0

    def is_critical_level(self):
        total = self.get_total_stock_count()
        return self.reorder_point >= total

    def is_overstock(self):
        stocks = self.get_total_stock_count()
        on_order = self.get_on_order_qty()
        total = stocks + on_order
        print(total > self.ceiling_qty)
        return total > self.ceiling_qty

    def get_qty_should_order(self):
        stocks = self.get_total_stock_count()
        on_order = self.get_on_order_qty()
        total = stocks + on_order
        should_order = 0
        if total < self.ceiling_qty:
            should_order = self.ceiling_qty - total
        return should_order

    def get_qty_to_reduce(self):
        stocks = self.get_total_stock_count()
        on_order = self.get_on_order_qty()
        total = stocks + on_order
        reduce_by = 0
        if total > self.ceiling_qty:
            reduce_by = total - self.ceiling_qty
        return reduce_by

    def get_latest_supplier_price(self):
        po = PO_Product.objects.filter(product=self).order_by('-pk').first()
        return po.unit_price

    def compute_prices(self, price):
        store = Store.objects.all().order_by('-pk').first()
        point_of_reference = store.point_of_reference
        retail_markup_below = store.retail_markup_below
        retail_markup = store.retail_markup
        wholesale_markup = store.wholesale_markup
        retail = 0
        wholesale = None
        if price < point_of_reference:
            retail = price * (1 + (retail_markup_below / 100))
        else:
            retail = price * (1 + (retail_markup / 100))
        if self.wholesale_qty > 0:
            wholesale = price * (1 + (wholesale_markup / 100)) * self.wholesale_qty
        return retail, wholesale

    def get_prices(self):
        price = self.get_latest_supplier_price()
        return self.compute_prices(price)

    def get_retail_price(self):
        retail, wholesale = self.get_prices()
        return retail

    def get_wholesale_price(self):
        retail, wholesale = self.get_prices()
        return wholesale

    def get_avg_supplier_price(self):
        avg_sprice_w = WarehouseStock.availableStocks.filter(product=self).aggregate(w_avg=Sum( F('supplier_price') * F('remaining_stocks')))['w_avg']
        avg_sprice_s = StoreStock.availableStocks.filter(product=self).aggregate(s_avg=Sum( F('supplier_price') * F('remaining_stocks')))['s_avg']
        count_w = WarehouseStock.availableStocks.filter(product=self).aggregate(w_count=Sum('remaining_stocks'))['w_count']
        count_s = StoreStock.availableStocks.filter(product=self).aggregate(s_count=Sum('remaining_stocks'))['s_count']
        if avg_sprice_w is None: avg_sprice_w = 0
        if avg_sprice_s is None: avg_sprice_s = 0
        if count_w is None: count_w = 0
        else: avg_sprice_w = avg_sprice_w / count_w
        if count_s is None: count_s = 0
        else: avg_sprice_s = avg_sprice_s / count_s
        if avg_sprice_w == 0:
            return avg_sprice_s
        elif avg_sprice_s == 0:
            return avg_sprice_w
        else:
            return (avg_sprice_s + avg_sprice_w) / 2

    def get_max_supplier_price(self):
        max_sprice_w = WarehouseStock.availableStocks.filter(product=self).aggregate(Max('supplier_price'))['supplier_price__max']
        max_sprice_s = StoreStock.availableStocks.filter(product=self).aggregate(Max('supplier_price'))['supplier_price__max']
        if max_sprice_w is None: max_sprice_w = 0
        if max_sprice_s is None: max_sprice_s = 0
        return max(max_sprice_s, max_sprice_w)

    def get_min_supplier_price(self):
        min_sprice_w = WarehouseStock.availableStocks.filter(product=self).aggregate(Min('supplier_price'))['supplier_price__min']
        min_sprice_s = StoreStock.availableStocks.filter(product=self).aggregate(Min('supplier_price'))['supplier_price__min']
        if min_sprice_w is None: min_sprice_w = 0
        if min_sprice_s is None: min_sprice_s = 0
        return min(min_sprice_s, min_sprice_w)

    def get_recommended_retail_price(self):
        max_price = self.get_max_supplier_price()
        retail, wholesale = self.compute_prices(max_price)
        if retail is None: retail = 0
        retail = float(int(retail*100)) / 100
        return round_up(retail)

    def get_recommended_wholesale_price(self):
        avg_price = self.get_max_supplier_price()
        retail, wholesale = self.compute_prices(avg_price)
        if wholesale is None: wholesale = 0
        wholesale = float(int(wholesale*100)) / 100
        return round_up(wholesale)

    def purchase(self, quantity, is_wholesale, cashier):
        if is_wholesale:
            quantity = quantity * self.wholesale_qty
        qty = quantity
        stocks = StoreStock.availableStocks.filter(product=self).order_by('pk')
        cogs = []
        for item in stocks:
            rem = item.remaining_stocks
            deducted = 0
            if rem >= qty:
                print(f"deducted {qty}")
                deducted = qty
                item.remaining_stocks = rem - qty
                item.save()
                
            else:
                print(f"deducted {rem}")
                deducted = rem
                qty = qty - rem
                item.remaining_stocks = 0
                item.save()

            cogs_item = (deducted, item)
            cogs.append(cogs_item)

            if qty == 0: break
        
        # record history
        hist = ProductHistory()
        hist.product = self
        hist.location = 1
        hist.quantity = 0 - quantity
        hist.remarks = 'Purchased.'
        hist.performed_by = cashier
        hist.save()

        return cogs

    class Meta:
        ordering = ['full_description']
    