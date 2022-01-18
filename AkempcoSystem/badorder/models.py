from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F
from fm.models import Supplier, Product
from django.contrib.auth.models import User

class BadOrder(models.Model):
    supplier = models.ForeignKey(
        Supplier, 
        verbose_name=_("Supplier"), 
        on_delete=models.CASCADE
    )
    date_discovered = models.DateField(
        _("Date Discovered"), 
        auto_now=True
    )
    reported_by = models.ForeignKey(
        User, 
        verbose_name=_("Reported By"), 
        related_name='bo_reporter',
        on_delete=models.RESTRICT
    )    
    date_approved = models.DateField(
        _("Date Approved"), 
        null=True,
        default=None
    )
    approved_by = models.ForeignKey(
        User, 
        verbose_name=_("Approved By"), 
        related_name='bo_approver',
        on_delete=models.RESTRICT,
        null=True,
        default=None
    )
    date_cancelled = models.DateField(
        _("Date Cancelled"), 
        null=True,
        default=None
    )
    cancelled_by = models.ForeignKey(
        User, 
        verbose_name=_("Cancelled By"), 
        related_name='bo_canceller',
        on_delete=models.RESTRICT,
        null=True,
        default=None
    )
    action_taken = models.CharField(
        _("Action Taken"), 
        max_length=100,
        null=True,
        default=None
    )

    class Meta:
        ordering = ['supplier', '-pk']

    def __str__(self):
        return self.supplier.supplier_name

    @property
    def number_of_items(self):
        return self.bo_items.all().count()

    @property
    def grand_total(self):
        return self.bo_items.all().aggregate(grand=Sum(F('quantity') * F('unit_price')))['grand']


class BadOrderItem(models.Model):
    bad_order = models.ForeignKey(
        BadOrder, 
        verbose_name=_("Bad Order"), 
        related_name='bo_items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, 
        verbose_name=_("Product"), 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField(_("Quantity"))
    unit_price = models.DecimalField(
        _("Unit Price"), 
        max_digits=8, 
        decimal_places=2
    )
    reason = models.CharField(
        _("Reason"), 
        max_length=100
    )

    @property
    def total_cost(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return str(self.quantity) + " " + self.product.uom.uom_description + \
            " of  " + self.product.full_description + " due to " + self.reason
    
    