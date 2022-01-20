from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F
from fm.models import Supplier, Product
from stocks.models import StoreStock, WarehouseStock, ProductHistory
from django.contrib.auth.models import User
from datetime import datetime


# BO_PROCESS class to monitor the steps in processing documents
class BO_PROCESS:
    STEPS = [
        (1, 'Pending'),
        (2, 'For Approval'),
        (3, 'Open'),
        (4, 'Closed'),
        (5, 'Rejected'),
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
    in_warehouse = models.BooleanField(
        _("Is this in the warehouse?"),
        help_text="True if BO is in the warehouse, otherwise it's in the store.",
        default=True
    )
    date_reported = models.DateField(
        _("Date Reported"), 
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
    date_rejected = models.DateField(
        _("Date Cancelled"), 
        null=True,
        default=None
    )
    rejected_by = models.ForeignKey(
        User, 
        verbose_name=_("Cancelled By"), 
        related_name='bo_canceller',
        on_delete=models.RESTRICT,
        null=True,
        default=None
    )
    reject_reason = models.CharField(
        _("Reject reason"), 
        max_length=250,
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

    def is_pending(self):
        return self.process_step == 1

    def is_for_approval(self):
        return self.process_step == 2

    def is_approved(self):
        return self.process_step == 3

    def is_closed(self):
        return self.process_step == 4
        
    def is_rejected(self):
        return self.process_step == 5

    def is_updatable(self):
        return self.process_step < 3 # not yet approved

    def get_status(self):
        for step in BO_PROCESS.STEPS:
            # return step
            if step[0] == self.process_step:
                return step[1]
        return None

    def get_product_qty(self, product):
        boi = BadOrderItem.objects.filter(bad_order=self, product=product)
        if boi:
            qty = boi.first().quantity
            boi.delete()
            return qty
        else:
            return 0

    def submit(self, user):
        self.reported_by = user
        self.in_warehouse = True if user.userdetail.userType == 'Warehouse Staff' else False
        self.process_step = 2 # For Approval
        self.save()

    def approve(self, user):
        # deduct all items in BadOrderItem from product warehouse stocks
        items = BadOrderItem.objects.filter(bad_order=self)
        total_price = 0
        price_count = 0
        for item in items:
            qty = item.quantity
            # deduct using FIFO
            while qty > 0:
                stock = None
                if self.in_warehouse:
                    stock = WarehouseStock.availableStocks.filter(product=item.product).order_by('pk').first()
                else:
                    stock = StoreStock.availableStocks.filter(product=item.product).order_by('pk').first()

                rem = stock.remaining_stocks
                deduct = 0 # how many items will be deducted in this record
                if rem >= qty:
                    deduct = qty
                    qty = 0
                else:
                    deduct = rem
                    qty = qty - rem

                # deduct qty from wh's remaining stocks
                stock.remaining_stocks = deduct
                stock.save()

                # update price info
                total_price = total_price + stock.supplier_price
                price_count = price_count + 1

            # update unit price
            item.unit_price = total_price / price_count
            item.save()

            # record in history
            hist = ProductHistory()
            hist.product = item.product
            hist.location = 0 if self.in_warehouse else 1
            hist.quantity = 0 - deduct
            hist.remarks = 'Bad order: ' + item.reason
            hist.performed_by = self.reported_by
            hist.save()
            
        # update fields of this record
        self.approved_by = user
        self.date_approved = datetime.now()
        self.process_step = 3 # Open (Approved)
        self.save()

    def reject(self, user, reason):
        self.rejected_by = user
        self.date_rejected = datetime.now()
        self.reject_reason = reason
        self.process_step = 5 # Rejected
        self.save()

    def close(self):
        self.process_step = 4 # Closed
        self.save()

    def save_action_taken(self, action, shouldClose = False):
        # if action is "Replaced by the supplier.", should increment the stocks back
        if action == 'Replaced by the supplier.':
            pass
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
        _("Average Unit Price"), 
        max_digits=8, 
        decimal_places=2,
        null=True,
        default=None
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
    
    