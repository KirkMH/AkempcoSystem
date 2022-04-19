from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F, Max, Min
import decimal
from datetime import datetime

from django.contrib.auth.models import User
from fm.models import Product
from admin_area.models import get_vatable_percentage, is_store_vatable
from stocks.models import StoreStock, ProductHistory


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
    necessity_only = models.BooleanField(
        _("For basic necessities or prime commodities only?"),
        help_text=_("Is this discount for basic necessities or prime commodities only?"),
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

    def compute(self, amount, count):
        if self.discount_type == 'peso':
            if count == 0:
                return self.value
            else:
                return self.value / count
        else:
            return amount * (self.value / 100)

    class Meta:
        ordering = ['name']


class XReading(models.Model):
    vat_removed = models.DecimalField(
        _('VAT Removed'),
        max_digits=10,
        decimal_places=2
    )
    discounts = models.DecimalField(
        _('Discounts'),
        max_digits=10,
        decimal_places=2
    )
    vatable = models.DecimalField(
        _('VATable Sales'),
        max_digits=10,
        decimal_places=2
    )
    vat = models.DecimalField(
        _('VAT Amount'),
        max_digits=10,
        decimal_places=2
    )
    vatex = models.DecimalField(
        _('VAT Exempt Sales'),
        max_digits=10,
        decimal_places=2
    )
    zero_rated = models.DecimalField(
        _('Zero Rated Sales'),
        max_digits=10,
        decimal_places=2
    )
    items_sold = models.PositiveIntegerField(
        _('Number of Items Sold')
    )
    transaction_count = models.PositiveIntegerField(
        _('Transaction Count')
    )
    void_count = models.PositiveIntegerField(
        _('Void Count')
    )
    void_total = models.DecimalField(
        _('Void Total'),
        max_digits=10,
        decimal_places=2
    )
    first_si = models.PositiveIntegerField(
        _('First Sales Invoice')
    )
    last_si = models.PositiveIntegerField(
        _('Last Sales Invoice')
    )
    created_at = models.DateTimeField(
        _("Created At"), 
        auto_now_add=True
    )
    created_by = models.ForeignKey(
        User,
        related_name='xreading_creator',
        verbose_name=_("Created By"),
        on_delete=models.CASCADE
    )
    total_sales = models.DecimalField(
        _("Total Sales"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    gross_sales = models.DecimalField(
        _("Gross Sales"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    vd_total_sales = models.DecimalField(
        _("VAT Detail Total"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )

    def fill_in_other_fields(self):
        self.total_sales = TenderReport.objects.filter(xreading=self).aggregate(val=Sum('amount'))['val']
        self.gross_sales = self.total_sales + self.vat_removed + self.discounts
        self.vd_total_sales = self.vatable + self.vat + self.vatex + self.zero_rated
        self.save()

    def __str__(self):
        return f"X-Reading #{self.pk} Total Sales: PhP{self.total_sales} at {self.created_at}"


class TenderReport(models.Model):
    xreading = models.ForeignKey(
        XReading,
        verbose_name=_('X-Reading'),
        on_delete=models.CASCADE
    )
    payment_mode = models.CharField(
        _('Payment Mode'),
        max_length=50
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.xreading} {self.payment_mode} {self.amount}"


class DiscountReport(models.Model):
    xreading = models.ForeignKey(
        XReading,
        verbose_name=_('X-Reading'),
        on_delete=models.CASCADE
    )
    discount = models.ForeignKey(
        Discount,
        verbose_name=_('Discount'),
        on_delete=models.CASCADE
    )
    total_vat = models.DecimalField(
        _('Total VAT'),
        max_digits=10,
        decimal_places=2,
        null=True
    )
    total_discount = models.DecimalField(
        _('Total Discount'),
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.xreading} {self.discount} {self.total_vat} {self.total_discount}"


class ZReadingValidation(models.Manager):
    def is_report_generated_today(self):
        return ZReading.objects.filter(xreading__created_at__date=datetime.date(datetime.now())).count() > 0

class ZReading(models.Model):
    xreading = models.OneToOneField(
        XReading,
        verbose_name=_('X-Reading'),
        on_delete=models.CASCADE
    )
    void_sales = models.DecimalField(
        _('Beginning Balance'),
        max_digits=10,
        decimal_places=2
    )
    beginning_bal = models.DecimalField(
        _('Beginning Balance'),
        max_digits=10,
        decimal_places=2
    )
    ending_bal = models.DecimalField(
        _('Ending Balance'),
        max_digits=10,
        decimal_places=2
    )
    transaction_count = models.PositiveIntegerField(_('Transaction Count'))
    objects = models.Manager()
    validations = ZReadingValidation()

    def __str__(self):
        return f"{self.xreading} from SI#{self.xreading.first_si} to SI#{self.xreading.last_si}"

    @property
    def created_at(self):
        return self.xreading.created_at

    @property
    def created_by(self):
        return self.xreading.created_by


class SalesReport(models.Manager):
    def generate_report(self, sales, cashier):
        # create a new x-reading report
        xreading = XReading()

        # SI numbers in the series
        xreading.first_si = SalesInvoice.objects.filter(sales__in=sales).aggregate(val=Min('id'))['val'] or 0
        xreading.last_si = SalesInvoice.objects.filter(sales__in=sales).aggregate(val=Max('id'))['val'] or 0

        # tender reconciliation - payment types
        tender_types = SalesPayment.objects.filter(sales__in=sales, sales__status='Completed') \
                    .values('payment_mode') \
                    .annotate(total_amount=Sum('value')) \
                    .order_by('payment_mode')
        xreading.vat_removed = SalesItem.objects \
                    .filter(sales__in=sales, sales__status='Completed') \
                    .aggregate(val=Sum('less_vat'))['val'] or 0
        xreading.discounts = SalesItem.objects \
                    .filter(sales__in=sales, sales__status='Completed') \
                    .aggregate(val=Sum('less_discount'))['val'] or 0

        # VAT declarations
        xreading.vatable = SalesItem.objects \
                    .filter(sales__in=sales, sales__status='Completed') \
                    .aggregate(val=Sum('vatable'))['val'] or 0
        xreading.vat = SalesItem.objects \
                    .filter(sales__in=sales, sales__status='Completed') \
                    .aggregate(val=Sum(F('vat_amount')-F('less_vat')))['val'] or 0
        xreading.vatex = SalesItem.objects \
                    .filter(sales__in=sales, sales__status='Completed') \
                    .aggregate(val=Sum('vat_exempt'))['val'] or 0
        xreading.zero_rated = SalesItem.objects \
                    .filter(sales__in=sales, sales__status='Completed') \
                    .aggregate(val=Sum('zero_rated'))['val'] or 0

        # cashier audit
        xreading.items_sold = SalesItem.objects \
                    .filter(sales__in=sales, sales__status='Completed') \
                    .aggregate(val=Sum('quantity'))['val'] or 0
        t_count = SalesItem.objects \
                    .filter(sales__in=sales, sales__status='Completed') \
                    .count() - 1
        xreading.transaction_count = t_count if t_count >= 0 else 0
        xreading.void_count = SalesVoid.objects \
                    .filter(sales_invoice__sales__in=sales) \
                    .count()
        xreading.void_total = SalesPayment.objects \
                    .filter(sales__in=sales, sales__status='Cancelled') \
                    .aggregate(val=Sum('value'))['val'] or 0

        xreading.created_by = cashier
        xreading.save()

        # save tender types
        for tender in tender_types:
            print(tender)
            TenderReport.objects.create(
                xreading=xreading,
                payment_mode=tender['payment_mode'],
                amount=tender['total_amount']
            )

        # for discounts
        discounts = Discount.objects.filter(active=True)
        # save discounts granted
        for disc in discounts:
            if disc:
                discount_rpt = DiscountReport()
                discount_rpt.xreading = xreading
                discount_rpt.discount = disc
                if disc.necessity_only:
                    discount_rpt.total_vat = SalesItem.objects \
                            .filter(sales__in=sales, sales__status='Completed', sales__discount_type=disc) \
                            .aggregate(val=Sum('less_vat'))['val'] or 0
                discount_rpt.total_discount = SalesItem.objects \
                        .filter(sales__in=sales, sales__status='Completed', sales__discount_type=disc) \
                        .aggregate(val=Sum('less_discount'))['val'] or 0  
                discount_rpt.save()

        return xreading

    def generate_xreading(self, cashier):
        last = cashier.userdetail.last_login
        if last == None: return None
        print(last)
        # query all Sales that happened from last login to now
        sales = Sales.objects.filter(salesinvoice__sales_datetime__gte=last)
        print(f"x-reading sales: {sales}")
        rpt = self.generate_report(sales, cashier)
        rpt.fill_in_other_fields()
        return rpt
        

    def generate_zreading(self, cashier):
        # check if a z-reading was already generated
        if ZReading.validations.is_report_generated_today():
            # do not continue with the transaction
            return False

        sales = Sales.objects.filter(
            salesinvoice__sales_datetime__date=datetime.date(datetime.now())
        )
        print(f"sales: {sales}")
        xreading = self.generate_report(sales, cashier)
        if xreading == None: return None

        # Create a new Z-Reading
        zreading = ZReading()
        zreading.xreading = xreading

        # get beginning balance
        beg_bal = 0
        beg_trans_count = 0
        beg_void = 0
        last_rec = ZReading.objects.last()
        if last_rec: 
            beg_bal = last_rec.ending_bal or 0
            beg_trans_count = last_rec.transaction_count or 0
            beg_void = last_rec.void_sales or 0

        print(f"beg_bal: {beg_bal}")
        zreading.void_sales = beg_void + xreading.void_total
        zreading.beginning_bal = beg_bal
        zreading.ending_bal = beg_bal + xreading.total_sales
        zreading.transaction_count = beg_trans_count + xreading.transaction_count
        print(f"zreading: {zreading}")
        zreading.save()
        return zreading
            

class Sales(models.Model):
    WIP = 'WIP'
    HOLD = 'On-Hold'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'
    STATUS_LIST = [
        (WIP, _('Work-in-Progress')),
        (HOLD, _('On-Hold')),
        (COMPLETED, _('Completed')),
        (CANCELLED, _('Cancelled')),
    ]

    discount_type = models.ForeignKey(
        Discount, 
        verbose_name=_("Discount Type"), 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    customer_name = models.CharField(
        _("Customer's Name"),
        max_length=150,
        null=True,
        blank=True,
        default=None
    )
    customer_address = models.CharField(
        _("Customer's Address"),
        max_length=150,
        null=True,
        blank=True,
        default=None
    )
    customer_id_card = models.CharField(
        _("Customer's ID number"),
        max_length=25,
        null=True,
        blank=True,
        default=None
    )
    customer_tin = models.CharField(
        _("Customer's TIN"),
        max_length=25,
        null=True,
        blank=True,
        default=None
    )
    customer = models.ForeignKey(
        "member.Creditor", 
        verbose_name=_("Customer"), 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    cashier = models.ForeignKey(
        User, 
        verbose_name=_("Cashier"), 
        on_delete=models.RESTRICT,
        null=True,
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
        default=WIP
    )
    discount = models.DecimalField(
        _("Discount"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    less_discount_total = models.DecimalField(
        _("Less Discount Total"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    less_vat_total = models.DecimalField(
        _("Less VAT Total"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        _("Grand Total, disregarding discounts"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    with_discount_total = models.DecimalField(
        _("Grand Total, considering discounts"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    sales_without_vat = models.DecimalField(
        _("Sales Without VAT"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    item_count = models.PositiveSmallIntegerField(
        _("Item Count"),
        default=0
    )
    vatable = models.DecimalField(
        _("Vatable"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    vat = models.DecimalField(
        _("VAT"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    zero_rated = models.DecimalField(
        _("Zero Rated"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    vat_exempt = models.DecimalField(
        _("VAT Exempt"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    payable = models.DecimalField(
        _("Payable"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    tendered = models.DecimalField(
        _("Tendered Amount"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    change = models.DecimalField(
        _("Change Amount"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    objects = models.Manager()
    reports = SalesReport()
    
    def __str__(self):
        return str(self.pk) + ": PhP " + str(self.payable)

    def fill_in_other_fields(self):
        self.less_discount_total = SalesItem.objects.filter(sales=self).aggregate(val=Sum('less_discount'))['val'] or 0
        self.less_vat_total = SalesItem.objects.filter(sales=self).aggregate(val=Sum('less_vat'))['val'] or 0
        self.total = SalesItem.objects.filter(sales=self).aggregate(val=Sum(F('unit_price') * F('quantity')))['val'] or 0
        self.with_discount_total = SalesItem.objects.filter(sales=self, less_discount__gt=0).aggregate(val=Sum(F('unit_price') * F('quantity')))['val'] or 0
        self.discount = self.less_discount_total + self.less_vat_total
        self.sales_without_vat = self.with_discount_total - self.less_vat_total
        self.item_count = SalesItem.objects.filter(sales=self).aggregate(val=Sum('quantity'))['val'] or 0
        self.vatable = SalesItem.objects.filter(sales=self, vatable__isnull=False).aggregate(val=Sum('vatable'))['val'] or 0
        self.vat = SalesItem.objects.filter(sales=self, vat_amount__isnull=False).aggregate(val=Sum('vat_amount'))['val'] or 0
        self.zero_rated = SalesItem.objects.filter(sales=self, zero_rated__isnull=False).aggregate(val=Sum('zero_rated'))['val'] or 0
        self.vat_exempt = SalesItem.objects.filter(sales=self, vat_exempt__isnull=False).aggregate(val=Sum('vat_exempt'))['val'] or 0
        self.payable = decimal.Decimal(self.total) - self.less_discount_total - self.less_vat_total
        self.tendered = SalesPayment.objects.filter(sales=self).aggregate(val=Sum('amount'))['val'] or 0
        print(self.tendered)
        self.change = self.tendered - self.payable
        self.save()

    @property
    def is_buyer_info_required(self):
        return SalesItem.objects.filter(sales=self, product__is_buyer_info_needed=True).count() > 0

    def get_next_si(self):
        si = SalesInvoice.objects.all().first()
        if si:
            return si.pk + 1
        else:
            return 1

    def clone(self, current):
        try:
            items = SalesItem.objects.filter(sales=self)
            for item in items:
                item.pk = None
                item.sales = current
                item.save()
                item.fill_in_other_fields()
            current.fill_in_other_fields()
            return True
        except:
            return False

    def reset(self):
        # delete all sales items under this transaction
        SalesItem.objects.filter(sales=self).delete()
        self.fill_in_other_fields()

    def apply_discount(self):
        if self.discount > 0:
            self.cancel_discount()
        # go over the entire SalesItem and apply discount accordingly,
        items = SalesItem.objects.filter(sales=self)
        count = items.count()
        if items:
            for item in items:
                item.apply_discount(self.discount_type, count)
        self.fill_in_other_fields()

    def cancel_discount(self):
        # get products and their quantity
        items = SalesItem.objects.filter(sales=self)
        prod_qty = []
        for item in items:
            pq = (item.product, item.quantity)
            prod_qty.append(pq)
        # delete all items
        items.delete()
        # add products with quantity
        for pq in prod_qty:
            self.add_product(pq[0].barcode, pq[1])

        # If the discount_type was set to none, reset customer details too
        print(self.discount_type)
        if self.discount_type == None:
            self.customer_name = None
            self.customer_address = None
            self.customer_id_card = None
            self.customer_tin = None
            self.save()
        self.fill_in_other_fields()


    def price_composition(self, product, subtotal):
        vatable = vat_amount = vat_exempt = zero_rated = decimal.Decimal(0)
        if product.tax_type == 'V': # VATable
            vat_percent = decimal.Decimal(get_vatable_percentage() / 100 + 1)
            vatable = subtotal / vat_percent
            vat_amount = subtotal - vatable
        elif product.tax_type == 'E': # VAT-Exempt
            vat_exempt = subtotal
        else: # Zero-Rated
            zero_rated = subtotal
        return vatable, vat_amount, vat_exempt, zero_rated

    def add_product(self, barcode, quantity):
        qty = quantity
        product = Product.objects.filter(barcode=barcode)[:1]
        if product:
            product = product.first()
            rem = product.store_stocks
            print(rem)
            if product.status != 'ACTIVE':
                return False, product.full_description + " is currently not active. Please make it active first."
            elif product.price_review == True or product.wholesale_price == None or product.selling_price == None:
                return False, product.full_description + " is currently for price review. The price must be approved first."
            elif rem < quantity:
                return False, "Insufficient stocks. <br>Remaining stocks is only " + str(rem) + "."
            else:
                # check if this product exists as wholesale
                item = SalesItem.objects.filter(sales=self, product=product, is_wholesale=True)
                if item:
                    first = item.first()
                    # get qty
                    qty = qty + first.quantity * product.wholesale_qty
                    item.delete()
                # check if this product exists as retail
                item = SalesItem.objects.filter(sales=self, product=product, is_wholesale=False)
                if item:
                    first = item.first()
                    # get qty and add it to qty
                    qty = qty + first.quantity
                    item.delete()
                
                # compute wholesale qty
                ws_qty = int(qty / product.wholesale_qty) if product.wholesale_qty > 0 else 0
                qty = qty - ws_qty * product.wholesale_qty
                if ws_qty > 0:
                    subtotal = ws_qty * product.wholesale_price
                    vatable, vat_amount, vat_exempt, zero_rated = self.price_composition(product, subtotal)
                    item = SalesItem.objects.create(
                        sales=self,
                        product=product,
                        quantity=ws_qty,
                        unit_price=product.wholesale_price,
                        is_wholesale=True,
                        vatable=vatable,
                        vat_amount=vat_amount,
                        vat_exempt=vat_exempt,
                        zero_rated=zero_rated
                    )
                    item.fill_in_other_fields()

                if qty > 0:
                    subtotal = qty * product.selling_price
                    vatable, vat_amount, vat_exempt, zero_rated = self.price_composition(product, subtotal)
                    item = SalesItem.objects.create(
                        sales=self,
                        product=product,
                        quantity=qty,
                        unit_price=product.selling_price,
                        is_wholesale=False,
                        vatable=vatable,
                        vat_amount=vat_amount,
                        vat_exempt=vat_exempt,
                        zero_rated=zero_rated
                    )
                    item.fill_in_other_fields()
                    
                message = ""
                if quantity < 0:
                    message = "Removed " + str(quantity * -1)
                else:
                    message = "Added " + str(quantity)

                self.fill_in_other_fields()

                return True, message + " " + product.uom.uom_description + "(s) of " + product.full_description + "."
        else:
            return False, "Barcode not found."

    def hold(self):
        self.status = Sales.HOLD
        self.save()

    def load(self):
        self.status = Sales.WIP
        self.save()

    def complete(self, cashier, details=None):
        invoice = SalesInvoice()
        invoice.sales = self
        invoice.details = details
        invoice.save()
        # adjust store stocks accordingly
        items = SalesItem.objects.filter(sales=self)
        if items:
            for item in items:
                cogs = item.product.purchase(item.quantity, item.is_wholesale, cashier)
                # save individual cogs
                for cogs_item in cogs:
                    stock = cogs_item[1]
                    qty = cogs_item[0]
                    price = stock.supplier_price
                    sic = SalesItemCogs()
                    sic.sales_item = item
                    sic.quantity = qty
                    sic.store_stock = stock
                    sic.selling_price = item.product.wholesale_price if item.is_wholesale else item.product.selling_price
                    sic.save()

        self.cashier = cashier
        self.status = Sales.COMPLETED
        self.save()
        return invoice.pk

    def set_customer(self, who):
        self.customer = who
        if who:
            self.customer_name = who.name
            self.customer_address = who.address
            self.customer_tin = who.tin
        else:
            self.customer_name = None
            self.customer_address = None
            self.customer_tin = None
        self.save()

    def get_customer(self):
        if self.customer == None:
            return 'Walk-in'
        else:
            return self.customer.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'Sales'
        verbose_name_plural = 'Sales'


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
    is_wholesale = models.BooleanField(
        _("Is wholesale?"),
        default=False
    )
    vatable = models.DecimalField(
        _("VATable"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    vat_amount = models.DecimalField(
        _("VAT Amount"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    vat_exempt = models.DecimalField(
        _("VAT-Exempt"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    zero_rated = models.DecimalField(
        _("Zero-Rated"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    less_vat = models.DecimalField(
        _("Less: VAT"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    less_discount = models.DecimalField(
        _("Less: Discount"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    subtotal = models.DecimalField(
        _("Subtotal"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        _("Total"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.product.full_description + ": " + str(self.quantity)

    def fill_in_other_fields(self):
        self.subtotal = self.unit_price * self.quantity
        
        less_vat = 0 if self.less_vat == None else self.less_vat
        less_discount = 0 if self.less_discount == None else self.less_discount
        self.total = self.subtotal - less_vat - less_discount

        self.save()

    def apply_discount(self, discount_type, count = 0):
        if not discount_type:
            return
        print(f"self.product.tax_type: {self.product.tax_type}")
        print(f"discount_type.necessity_only: {discount_type.necessity_only}")
        print(f"self.product.for_discount: {self.product.for_discount}")
        # check if the tax is VATable, and for necessity
        if self.product.tax_type == 'V' \
            and discount_type.necessity_only and self.product.for_discount:
            # print(self.product)
            self.less_vat = self.vat_amount # the entire VAT will be deducted
            discount_amt = discount_type.compute(self.vatable, count)
            self.less_discount = discount_amt
            self.vat_exempt = self.vatable - discount_amt  # the product will become VAT-Exempt less discount
            self.vatable = 0
            print("Discount-1 Applied")
            print(f" self.less_vat: {self.less_vat}")
            print(f" self.vat_exempt: {self.vat_exempt}")
            print(f" self.less_discount: {self.less_discount}")
        # apply discount for non-VATable products, or when not for necessity
        elif (discount_type.necessity_only and self.product.for_discount) \
            or not discount_type.necessity_only:
            print("Discount-2 Applied")
            self.less_discount = discount_type.compute(self.subtotal, count)
            if self.vatable > 0:
                self.vatable = self.vatable - self.less_discount
            elif self.vat_exempt > 0:
                self.vat_exempt = self.vat_exempt - self.less_discount
            else:
                self.zero_rated = self.zero_rated - self.less_discount
        else:
            print("No Discount Applied")
            self.less_vat = 0
            self.less_discount = 0
        self.save()
        self.fill_in_other_fields()


    class Meta:
        ordering = ['product']


# used for monitoring cogs per sold item
# due to the possibility of getting a product
# from different supplier prices
class SalesItemCogs(models.Model):
    sales_item = models.ForeignKey(
        SalesItem, 
        verbose_name=_("Sales Item"), 
        on_delete=models.CASCADE
    )
    store_stock = models.ForeignKey(
        StoreStock, 
        verbose_name=_("Store Stock Reference"), 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(_("Quantity"))
    selling_price = models.DecimalField(
        _("Selling Price"), 
        max_digits=8, 
        decimal_places=2
    )

    @property
    def cogs(self):
        return self.store_stock.supplier_price

    @property
    def gross_profit(self):
        return self.quantity * (self.selling_price - self.cogs)

    def __str__(self):
        return self.sales_item.product.full_description + "\n" + \
            "Quantity: " + str(self.quantity) + "\n" + \
            "COGS: " + str(self.cogs) + "\n" + \
            "Selling Price: " + str(self.selling_price) + "\n" + \
            "Gross Profit: " + str(self.gross_profit)
    


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
    details = models.TextField(
        _("Details"), 
        null=True,
        blank=True,
        default=None)

    @property
    def si_date(self):
        return self.sales_datetime.date()

    @property 
    def si_time(self):
        return self.sales_datetime.time()

    @property
    def is_cancelled(self):
        return SalesVoid.objects.filter(sales_invoice=self).exists()

    def get_payment_modes(self):
        return list(self.sales.salespayment_set.order_by().values_list('payment_mode', flat=True).distinct())

    def get_payment_modes_as_string(self):
        modes = self.get_payment_modes()
        return ', '.join(modes)

    def reprint(self, cashier):
        self.last_reprint = datetime.now()
        self.reprint_by = cashier
        self.save()

    def cancel(self, cashier, approver):
        # cancel parent sales record
        self.sales.status = Sales.CANCELLED
        self.sales.save()
        # create SalesVoid for Void Transaction Number
        void = SalesVoid()
        void.sales_invoice = self
        void.cancelled_on = datetime.now()
        void.cancelled_by = cashier
        void.approved_by = approver
        void.save()
        # Return products to store
        sales_items = SalesItem.objects.filter(sales=self.sales)
        print(sales_items)
        for sales_item in sales_items:
            sics = SalesItemCogs.objects.filter(sales_item=sales_item)
            print(sales_item)
            print(sics)
            for sic in sics:
                # return quantity to where it came from
                sic.store_stock.remaining_stocks = sic.store_stock.remaining_stocks + sic.quantity
                sic.store_stock.save()
                print(sic.store_stock.remaining_stocks)
            # record this in the history
            hist = ProductHistory()
            hist.product = sales_item.product
            hist.location = 1 # Store
            hist.quantity = sales_item.quantity
            hist.remarks = "Cancelled sales invoice."
            hist.performed_on = datetime.now()
            hist.performed_by = cashier
            hist.save()
            print(hist)

        return void.pk

    class Meta:
        ordering = ['-pk']


class SalesVoid(models.Model):
    sales_invoice = models.OneToOneField(
        SalesInvoice, 
        verbose_name=_("Sales Invoice"), 
        related_name="sales_void",
        on_delete=models.CASCADE
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
    approved_by = models.ForeignKey(
        User, 
        verbose_name=_("Approved by"), 
        related_name='si_cancellation_approver',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )

    def __str__(self):
        return "Cancelled by " + self.cancelled_by.full_name + " on " + str(self.cancelled_on)
    


class SalesPayment(models.Model):
    CASH = 'Cash'
    CHEQUE = 'Cheque'
    CHARGE = 'Charge'
    GC = 'Gift Certificate'
    EMONEY = 'E-Money'
    CARD = 'Debit/Credit Card'
    MODE_CHOICES = [
        (CASH, _(CASH)),
        (CHEQUE, CHEQUE),
        (CHARGE, CHARGE),
        (GC, GC),
        (EMONEY, EMONEY),
        (CARD, CARD)
    ]
    sales = models.ForeignKey(
        Sales, 
        verbose_name=_("Sales Record"), 
        on_delete=models.CASCADE
    )
    payment_mode = models.CharField(
        _("Payment Mode"), 
        max_length=20,
        choices=MODE_CHOICES,
        default=CASH
    )
    details = models.CharField(
        _("Payment Details"), 
        max_length=50,
        null=True,
        blank=True,
        default=None
    )
    amount = models.DecimalField(
        _("Amount Tendered"), 
        max_digits=8,
        decimal_places=2
    )
    value = models.DecimalField(
        _("Accepted Value"), 
        max_digits=8,
        decimal_places=2,
        null=True
    )

    def __str__(self):
        if self.details:
            return self.payment_mode + " (" + self.details + "): PhP" + str(self.amount)
        else:
            return self.payment_mode + ": PhP" + str(self.amount)    