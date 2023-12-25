from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Min, Max, Sum, F, Q
from django.apps import apps
import math
from datetime import datetime
from dateutil import relativedelta

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
    ZERORATED = 'Zero-Rated'
    TAX_CLASSIFICATION = [
        (TAXABLE, _('Taxable')),
        (NONTAX, _('Non-Taxable')),
        (TAXEXEMPT, _('Tax Exempt')),
        (ZERORATED, _('Zero-Rated'))
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
    last_po = models.OneToOneField(
        "purchases.PurchaseOrder",
        related_name='last_po',
        verbose_name=_("Last Purchase Order"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    po_count = models.PositiveIntegerField(
        _("Number of Purchase Orders"),
        default=0
    )
    open_po_count = models.PositiveIntegerField(
        _("Number of Open Purchase Orders"),
        default=0
    )
    completion_rate = models.FloatField(
        _("Completion Rate"),
        default=0
    )

    def __str__(self):
        return self.supplier_name

    def fill_in_other_fields(self):
        self.open_po_count = PurchaseOrder.objects.filter(
            supplier=self).filter(is_open=True, process_step__lt=6).count() or 0
        self.po_count = PurchaseOrder.objects.filter(
            supplier=self, process_step__lt=6).count() or 0
        if self.po_count > 0:
            closed_ctr = self.po_count - self.open_po_count
            self.completion_rate = closed_ctr / self.po_count
        self.save()

    def get_completion_rate(self):
        try:
            open_ctr = self.open_po_count
            po_ctr = self.po_count
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
        help_text=_(
            "The level (quantity) when you will need to place an order so you won't run out of stock.")
    )
    ceiling_qty = models.PositiveIntegerField(
        _("Ceiling Quantity"),
        default=50,
        help_text=_(
            "The maximum quantity you should keep in inventory in order to meet your demand and avoid overstocking.")
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
        help_text=_(
            "Is this a basic necessity or prime commodity? SC and PWD discounts will be applied."),
        default=False
    )
    is_consignment = models.BooleanField(
        _("Consigned product?"),
        help_text=_("Is this a consigned product?"),
        default=False
    )
    is_buyer_info_needed = models.BooleanField(
        _("Buyer's information needed?"),
        help_text=_(
            "Do you need to get the buyer's information upon purchase?"),
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
        blank=True,
        default=None
    )
    cancelled_at = models.DateTimeField(
        _("Cancelled at"),
        null=True,
        blank=True,
        default=None
    )
    suppliers = models.ManyToManyField(Supplier)
    status = models.CharField(
        _("Status"),
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )
    warehouse_stocks = models.PositiveIntegerField(
        _("Warehouse Stocks"),
        default=0
    )
    store_stocks = models.PositiveIntegerField(
        _("Store Stocks"),
        default=0
    )
    total_stocks = models.PositiveIntegerField(
        _("Total Stocks"),
        default=0
    )
    latest_supplier_price = models.DecimalField(
        _("Latest Supplier Price"),
        max_digits=11,
        decimal_places=2,
        default=0,
        null=True,
        blank=True
    )
    # for the Inventory Turnover Ratio
    cogs = models.DecimalField(
        _("Cost of Goods Sold"),
        max_digits=11,
        decimal_places=2,
        default=0,
        null=True,
        blank=True
    )
    avg_inventory = models.DecimalField(
        _("Average Inventory"),
        max_digits=11,
        decimal_places=2,
        default=0,
        null=True,
        blank=True
    )
    itr = models.DecimalField(
        _("Inventory Turnover Ratio"),
        max_digits=11,
        decimal_places=2,
        default=0,
        null=True,
        blank=True
    )

    @property
    def tax_type_description(self):
        for tt in self.TAXTYPE:
            if tt[0] == self.tax_type:
                return tt[1]
        return ''

    def __str__(self):
        return self.full_description

    def compute_itr(self):
        # prepare models
        SalesVoid = apps.get_model('sales', 'SalesVoid')
        Sales = apps.get_model('sales', 'Sales')
        SalesItem = apps.get_model('sales', 'SalesItem')
        SalesItemCogs = apps.get_model('sales', 'SalesItemCogs')
        # computing cogs for the last 1 month
        last_month = datetime.now() + relativedelta.relativedelta(months=-1)
        print(f"last month: {last_month}")
        voided = SalesVoid.objects.filter(
            cancelled_on__gte=last_month).values('sales_invoice')
        sales = Sales.objects.filter(transaction_datetime__gte=last_month).exclude(
            salesinvoice__pk__in=voided)
        print(sales)
        sales_items = SalesItem.objects.filter(sales__in=sales, product=self)
        computed_cogs = SalesItemCogs.objects.filter(sales_item__in=sales_items) \
            .prefetch_related('store_stock') \
            .aggregate(cogs=Sum(F('quantity') * F('store_stock__supplier_price')))['cogs'] or 0
        # computing ending inventory
        ws_ending_bal = WarehouseStock.availableStocks.filter(product=self) \
            .aggregate(ws=Sum(F('supplier_price') * F('remaining_stocks')))['ws'] or 0
        ss_ending_bal = StoreStock.availableStocks.filter(product=self) \
            .aggregate(ss=Sum(F('supplier_price') * F('remaining_stocks')))['ss'] or 0
        ending_inv = ws_ending_bal + ss_ending_bal
        # computing purchases for the last 1 month
        po_list = PurchaseOrder.objects.filter(
            is_open=False, received_date__gte=last_month)
        purchases = PO_Product.objects.filter(purchase_order__in=po_list, product=self) \
            .aggregate(purchases=Sum(F('unit_price') * F('received_qty')))['purchases'] or 0
        # computing beginning inventory, average inventory, and itr
        beg_inv = ending_inv + computed_cogs - purchases
        computed_avg_inventory = (beg_inv + ending_inv) / 2
        computed_itr = computed_cogs / computed_avg_inventory
        # save computed results
        self.cogs = computed_cogs
        self.avg_inventory = computed_avg_inventory
        self.itr = computed_itr
        self.save()

        print(
            f"{self.full_description}: {ss_ending_bal} + {ws_ending_bal} = {ending_inv}, {purchases}")
        print(
            f"\t{computed_cogs} / (({beg_inv} + {ending_inv}) / 2) = {computed_itr}")

    def is_consigned(self):
        return 'Yes' if self.is_consignment else 'No'

    def is_buyer_info_required(self):
        return 'Yes' if self.is_buyer_info_needed else 'No'

    def set_stock_count(self):
        s_stocks = StoreStock.availableStocks.filter(
            product=self).aggregate(total=Sum('remaining_stocks'))['total']
        if s_stocks is None:
            s_stocks = 0

        w_stocks = WarehouseStock.availableStocks.filter(
            product=self).aggregate(total=Sum('remaining_stocks'))['total']
        if w_stocks is None:
            w_stocks = 0

        self.store_stocks = s_stocks
        self.warehouse_stocks = w_stocks
        self.total_stocks = s_stocks + w_stocks
        self.save()

    def get_on_order_qty(self):
        qty = PO_Product.objects.filter(
            Q(product=self) &
            Q(purchase_order__is_open=True) &
            Q(purchase_order__process_step__gt=1) &
            Q(purchase_order__process_step__lt=6)
        ).aggregate(on_order=Sum('ordered_quantity'))['on_order']
        return qty if qty else 0

    def is_critical_level(self):
        total = self.total_stocks
        return self.reorder_point >= total

    def is_overstock(self):
        stocks = self.total_stocks
        on_order = self.get_on_order_qty()
        total = stocks + on_order
        print(total > self.ceiling_qty)
        return total > self.ceiling_qty

    def get_qty_should_order(self):
        stocks = self.total_stocks
        on_order = self.get_on_order_qty()
        total = stocks + on_order
        should_order = 0
        if total < self.ceiling_qty:
            should_order = self.ceiling_qty - total
        return should_order

    def get_qty_to_reduce(self):
        stocks = self.total_stocks
        on_order = self.get_on_order_qty()
        total = stocks + on_order
        reduce_by = 0
        if total > self.ceiling_qty:
            reduce_by = total - self.ceiling_qty
        return reduce_by

    def get_earliest_supplier_price_with_stock(self):
        stock = WarehouseStock.availableStocks.filter(
            product=self).order_by('pk').first()
        supplier_price = stock.supplier_price
        return supplier_price

    def set_latest_supplier_price(self):
        po = PO_Product.objects.filter(
            product=self, purchase_order__status='Closed').order_by('-pk').first()
        self.latest_supplier_price = po.unit_price if po else 0
        self.save()

    def compute_prices(self, price):
        retail = None
        wholesale = None
        try:
            store = Store.objects.all().order_by('-pk').first()
            point_of_reference = store.retail_point_of_reference
            retail_markup_below = store.retail_markup_below
            retail_markup = store.retail_markup
            wholesale_markup = store.wholesale_markup
            if price < point_of_reference:
                retail = price * (1 + (retail_markup_below / 100))
            else:
                retail = price * (1 + (retail_markup / 100))
            if self.wholesale_qty > 0:
                if self.wholesale_price < store.wholesale_point_of_reference:
                    wholesale = self.wholesale_price * \
                        (1 + (store.wholesale_markup_below / 100))
                else:
                    wholesale = self.wholesale_price * \
                        (1 + (store.wholesale_markup / 100))
        except Exception as e:
            print(e)
        print(f"retail: {retail}, wholesale: {wholesale}")
        return retail, wholesale

    def get_prices(self):
        price = self.get_latest_supplier_price()
        return self.compute_prices(price)

    def get_retail_price(self):
        retail, _ = self.get_prices()
        return retail

    def get_wholesale_price(self):
        _, wholesale = self.get_prices()
        return wholesale

    def get_avg_supplier_price(self):
        avg_sprice_w = WarehouseStock.availableStocks.filter(product=self).aggregate(
            w_avg=Sum(F('supplier_price') * F('remaining_stocks')))['w_avg']
        avg_sprice_s = StoreStock.availableStocks.filter(product=self).aggregate(
            s_avg=Sum(F('supplier_price') * F('remaining_stocks')))['s_avg']
        count_w = WarehouseStock.availableStocks.filter(
            product=self).aggregate(w_count=Sum('remaining_stocks'))['w_count']
        count_s = StoreStock.availableStocks.filter(product=self).aggregate(
            s_count=Sum('remaining_stocks'))['s_count']
        if avg_sprice_w is None:
            avg_sprice_w = 0
        if avg_sprice_s is None:
            avg_sprice_s = 0
        if count_w is None:
            count_w = 0
        else:
            avg_sprice_w = avg_sprice_w / count_w
        if count_s is None:
            count_s = 0
        else:
            avg_sprice_s = avg_sprice_s / count_s
        if avg_sprice_w == 0:
            return avg_sprice_s
        elif avg_sprice_s == 0:
            return avg_sprice_w
        else:
            return (avg_sprice_s + avg_sprice_w) / 2

    def get_max_supplier_price(self):
        max_sprice_w = WarehouseStock.availableStocks.filter(
            product=self).aggregate(Max('supplier_price'))['supplier_price__max']
        max_sprice_s = StoreStock.availableStocks.filter(
            product=self).aggregate(Max('supplier_price'))['supplier_price__max']
        if max_sprice_w is None:
            max_sprice_w = 0
        if max_sprice_s is None:
            max_sprice_s = 0
        return max(max_sprice_s, max_sprice_w)

    def get_min_supplier_price(self):
        min_sprice_w = WarehouseStock.availableStocks.filter(
            product=self).aggregate(Min('supplier_price'))['supplier_price__min']
        min_sprice_s = StoreStock.availableStocks.filter(
            product=self).aggregate(Min('supplier_price'))['supplier_price__min']
        if min_sprice_w is None:
            min_sprice_w = 0
        if min_sprice_s is None:
            min_sprice_s = 0
        return min(min_sprice_s, min_sprice_w)

    def get_recommended_retail_price(self):
        max_price = self.get_max_supplier_price()
        retail, _ = self.compute_prices(max_price)
        if retail is None:
            retail = 0
        retail = float(int(retail*100)) / 100
        return round_up(retail)

    def get_recommended_wholesale_price(self):
        avg_price = self.get_max_supplier_price()
        _, wholesale = self.compute_prices(avg_price)
        if wholesale is None:
            wholesale = 0
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
                qty = 0

            else:
                print(f"deducted {rem}")
                deducted = rem
                qty = qty - rem
                item.remaining_stocks = 0
                item.save()

            cogs_item = (deducted, item)
            cogs.append(cogs_item)

            if qty == 0:
                break

        # record history
        hist = ProductHistory()
        hist.product = self
        hist.location = 1
        hist.quantity = 0 - quantity
        hist.remarks = 'Purchased.'
        hist.performed_by = cashier
        hist.save()
        hist.set_current_balance()

        return cogs

    class Meta:
        ordering = ['full_description']
