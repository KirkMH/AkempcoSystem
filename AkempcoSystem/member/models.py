from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F

from django.contrib.auth.models import User
from sales.models import Sales, SalesPayment, SalesItem, SalesInvoice


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
    total_charges = models.DecimalField(
        _("Total Charges"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    transaction_count = models.PositiveIntegerField(
        _("Transaction Count"), 
        default=0
    )
    total_transaction_amount = models.DecimalField(
        _("Total Transaction Amount"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    total_payments = models.DecimalField(
        _("Total Payments"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    remaining_credit = models.DecimalField(
        _("Remaining Credit"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    payable = models.DecimalField(
        _("Payable"), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )

    objects = models.Manager()
    members = MemberCreditors()
    groups = GroupCreditors()

    def fill_in_other_fields(self):
        charges = 0
        sales = Sales.objects.filter(customer=self, status='Completed').values_list('pk', flat=True)
        records = SalesPayment.objects.all()
        if records and sales:
            records = records.filter(sales__in=list(sales), payment_mode='Charge')
            charges = records.aggregate(s_amt=Sum('amount'))['s_amt']
        self.total_charges = charges

        sales = Sales.objects.filter(customer=self, status='Completed')
        self.transaction_count = sales.count() if sales else 0

        sales = Sales.objects.filter(customer=self, status='Completed').values_list('pk', flat=True)
        total = SalesItem.objects.filter(sales__in=sales).aggregate(val=Sum(F('unit_price') * F('quantity')))['val']
        self.total_transaction_amount = total if total else 0
        
        self.total_payments = CreditorPayment.objects.filter(creditor=self).aggregate(val=Sum('amount'))['val'] or 0

        self.payable = self.total_charges - self.total_payments
        
        self.remaining_credit = self.credit_limit - self.payable
        self.save()


    def get_latest_10_transactions(self):
        sales = Sales.objects.filter(customer=self, status='Completed').values_list('pk', flat=True)
        transactions = SalesInvoice.objects.filter(sales__in=sales).order_by('-sales_datetime')[:10]
        return transactions

    def get_all_transactions(self):
        sales = Sales.objects.filter(customer=self, status='Completed').values_list('pk', flat=True)
        transactions = SalesInvoice.objects.filter(sales__in=sales).order_by('-sales_datetime')
        return transactions

    def get_latest_10_payments(self):
        return CreditorPayment.objects.filter(creditor=self)[:10]

    def get_all_payments(self):
        return CreditorPayment.objects.filter(creditor=self)


    def __str__(self):
        return self.name + ": " + str(self.remaining_credit) + " of " + str(self.credit_limit)
    

    class Meta:
        ordering = ['name']


class CreditorPayment(models.Model):
    creditor = models.ForeignKey(
        Creditor,
        verbose_name=_('Creditor'),
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        _("Amount Paid"), 
        max_digits=10, 
        decimal_places=2
    )
    date_posted = models.DateField(
        _("Date Posted"),
        auto_now_add=True
    )
    posted_by = models.ForeignKey(
        User,
        verbose_name=_('Posted by'),
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.creditor.name} paid {self.amount} posted on {self.date_posted}"

    class Meta:
        ordering = ['-date_posted']
    