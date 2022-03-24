from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F

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

    @property
    def transaction_count(self):
        sales = Sales.objects.filter(customer=self, status='Completed')
        return sales.count() if sales else 0

    @property
    def total_transaction_amount(self):
        sales = Sales.objects.filter(customer=self, status='Completed').values_list('pk', flat=True)
        total = SalesItem.objects.filter(sales__in=sales).aggregate(val=Sum(F('unit_price') * F('quantity')))['val']
        return total if total else 0
        
    # TODO: total payments
    @property
    def total_payments(self):
        return 0

    
    @property
    def remaining_credit(self):
        total_charges = self.total_charges
        total_payments = self.total_payments

        return self.credit_limit - total_charges - total_payments

    def get_latest_10_transactions(self):
        sales = Sales.objects.filter(customer=self, status='Completed').values_list('pk', flat=True)
        transactions = SalesInvoice.objects.filter(sales__in=sales).order_by('-sales_datetime')[:10]
        return transactions

    def get_all_transactions(self):
        sales = Sales.objects.filter(customer=self, status='Completed').values_list('pk', flat=True)
        transactions = SalesInvoice.objects.filter(sales__in=sales).order_by('-sales_datetime')
        return transactions


    def __str__(self):
        return self.name + ": " + str(self.remaining_credit) + " of " + str(self.credit_limit)
    

    class Meta:
        ordering = ['name']
