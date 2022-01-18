from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F
from fm.models import Supplier, Product
from django.contrib.auth.models import User
from datetime import datetime


# BO_PROCESS class to monitor the steps in processing documents
class BO_PROCESS:
    STEPS = [
        (1, 'Pending'),
        (2, 'Approved'),
        (3, 'Closed'),
    ]


class BadOrder(models.Model):
    supplier = models.ForeignKey(
        Supplier, 
        verbose_name=_("Supplier"), 
        on_delete=models.CASCADE
    )
    date_discovered = models.DateField(
        _("Date Discovered"), 
        auto_now=False,
        auto_now_add=False
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
    process_step = models.PositiveSmallIntegerField(
        _("Process Step"),
        default=1 #Pending
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

    def is_approved(self):
        return self.process_step == 2

    def get_status(self):
        for step in BO_PROCESS.STEPS:
            # return step
            if step[0] == self.process_step:
                return step[1]
        return None

    def approve(self, user):
        self.approved_by = user
        self.date_approved = datetime.now()
        self.process_step = 2 # Approved
        self.save()
        # deduct all items in BadOrderItem from product warehouse stocks
        items = BadOrderItem.objects.filter(bad_order=self)
        for item in items:
            qty = item.quantity
            # deduct using FIFO
            while qty > 0:
                whs = WarehouseStock.availableStocks.filter(product=item.product).order_by('pk').first()
                rem = whs.remaining_stocks
                deduct = 0 # how many items will be deducted in this record
                if rem >= qty:
                    deduct = qty
                    qty = 0
                else:
                    deduct = rem
                    qty = qty - rem

                # deduct qty from wh's remaining stocks
                whs.remaining_stocks = deduct
                whs.save()

            # record in history
            hist = ProductHistory()
            hist.product = item.product
            hist.location = 0
            hist.quantity = 0 - deduct
            hist.remarks = 'Bad order.'
            hist.performed_by = self.reported_by
            hist.save()

    def close(self):
        self.process_step = 3 # Closed
        self.save()

    def save_action_taken(self, action, shouldClose = False):
        self.action_taken = action
        self.save()
        if shouldClose:
            self.close()


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
    
    