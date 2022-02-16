from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
import decimal

from django.contrib.auth.models import User
from fm.models import Product
from admin_area.models import get_vatable_percentage


class MemberCreditors(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(creditor_type='Member', active=True).order_by('name')

class GroupCreditors(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(creditor_type='Group', active=True).order_by('name')

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
    tin = models.CharField(
        _("Tax Identification Number"), 
        max_length=20,
        blank=True,
        null=True,
        default=None
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

    objects = models.Manager()
    members = MemberCreditors()
    groups = GroupCreditors()

    @ property
    def total_charges(self):
        total_charges = 0
        sales = Sales.objects.filter(customer=self, status='Completed').values_list('pk', flat=True)
        records = SalesPayment.objects.all()
        if records and sales:
            records = records.filter(sales__in=list(sales), payment_mode='Charge')
            total_charges = records.aggregate(s_amt=Sum('amount'))['s_amt']

        return total_charges

        
    # TODO: total payments
    @property
    def total_payments(self):
        return 0

    
    @property
    def remaining_credit(self):
        total_charges = self.total_charges
        total_payments = self.total_payments

        return self.credit_limit - total_charges - total_payments


    def __str__(self):
        return self.name + ": " + str(self.remaining_credit) + " of " + str(self.credit_limit)
    

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
    
    def __str__(self):
        return str(self.pk) + ": PhP " + str(self.payable)

    # helper method to compute total of items
    def compute_total(self, items):
        total = 0.0
        if items:
            for item in items:
                total = decimal.Decimal(total) + item.subtotal
        return total

    @property
    def total(self):
        items = SalesItem.objects.filter(sales=self)
        return self.compute_total(items)

    @property
    def item_count(self):
        return SalesItem.objects.filter(sales=self).count()

    @property
    def vatable(self):
        items = SalesItem.objects.filter(sales=self, product__tax_type='V')
        # this is the total with VAT
        total = self.compute_total(items)
        # less the VAT
        print(get_vatable_percentage())
        vat_p = 1 + get_vatable_percentage()
        return total / vat_p
       
    @property
    def vat(self):
        items = SalesItem.objects.filter(sales=self, product__tax_type='V')
        # this is the total with VAT
        total = self.compute_total(items)
        # less the VAT
        print(get_vatable_percentage())
        vat_p = 1 + get_vatable_percentage()
        return total - (total / vat_p)

    @property
    def zero_rated(self):
        items = SalesItem.objects.filter(sales=self, product__tax_type='Z')
        total = self.compute_total(items)
        return total

    @property
    def vat_exempt(self):
        items = SalesItem.objects.filter(sales=self, product__tax_type='E')
        total = self.compute_total(items)
        return total

    @property
    def payable(self):
        return decimal.Decimal(self.total) - self.discount

    @property
    def tendered(self):
        payments = SalesPayment.objects.filter(sales=self)
        total = 0
        if payments:
            for payment in payments:
                total = total + payment.amount
        return total

    @property
    def change(self):
        return self.tendered - self.payable

    def get_next_si(self):
        si = SalesInvoice.objects.all()[:1]
        if si:
            si = si.first()
            return si.pk + 1
        else:
            return 1

    def add_product(self, barcode, quantity):
        qty = quantity
        product = Product.objects.filter(barcode=barcode)[:1]
        if product:
            product = product.first()
            rem = product.get_store_stock_count()
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
                    item = SalesItem.objects.create(
                        sales=self,
                        product=product,
                        quantity=ws_qty,
                        unit_price=product.wholesale_price,
                        is_wholesale=True
                    )
                if qty > 0:
                    item = SalesItem.objects.create(
                        sales=self,
                        product=product,
                        quantity=qty,
                        unit_price=product.selling_price,
                        is_wholesale=False
                    )
                message = ""
                if quantity < 0:
                    message = "Removed " + str(quantity * -1)
                else:
                    message = "Added " + str(quantity)
                return True, message + " " + product.uom.uom_description + "(s) of " + product.full_description + "."
        else:
            return False, "Barcode not found."

    def hold(self):
        self.status = Sales.HOLD
        self.save()

    def load(self):
        self.status = Sales.WIP
        self.save()

    def add_payment(self, mode, detail, amount):
        payment = SalesPayment.objects.create(
            sales=self, 
            amount=amount, 
            payment_mode=mode, 
            details=detail
        )

    def complete(self, cashier):
        invoice = SalesInvoice()
        invoice.sales = self
        invoice.save()
        # adjust store stocks accordingly
        items = SalesItem.objects.filter(sales=self)
        if items:
            for item in items:
                cogs = item.product.purchase(item.quantity, item.is_wholesale, cashier)
                # save individual cogs
                for cogs_item in cogs:
                    qty = cogs_item[0]
                    price = cogs_item[1]
                    sic = SalesItemCogs()
                    sic.sales_item = item
                    sic.quantity = qty
                    sic.cogs = price
                    sic.selling_price = item.product.wholesale_price if item.is_wholesale else item.product.selling_price
                    sic.save()

        self.cashier = cashier
        self.status = Sales.COMPLETED
        self.save()
        return invoice.pk

    def set_customer(self, who):
        self.customer = who
        self.save()

    def get_customer(self):
        if self.customer == None:
            return 'Walk-in'
        else:
            return self.customer.name

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


# used for monitoring cogs per sold item
# due to the possibility of getting a product
# from different supplier prices
class SalesItemCogs(models.Model):
    sales_item = models.ForeignKey(
        SalesItem, 
        verbose_name=_("Sales Item"), 
        on_delete=models.CASCADE
    )
    cogs = models.DecimalField(
        _("Cost of Goods Sold"), 
        max_digits=8, 
        decimal_places=2
    )
    quantity = models.PositiveIntegerField(_("Quantity"))
    selling_price = models.DecimalField(
        _("Selling Price"), 
        max_digits=8, 
        decimal_places=2
    )

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

    @property
    def si_date(self):
        return self.sales_datetime.date()

    @property 
    def si_time(self):
        return self.sales_datetime.time()

    class Meta:
        ordering = ['-pk']


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

    def __str__(self):
        if self.details:
            return self.payment_mode + " (" + self.details + "): PhP" + str(self.amount)
        else:
            return self.payment_mode + ": PhP" + str(self.amount)    