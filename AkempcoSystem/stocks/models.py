from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# RV_PROCESS class to monitor the steps in processing documents
class RV_PROCESS:
    STEPS = [
        (1, 'Pending'),
        (2, 'For Approval'),
        (3, 'Approved'),
        (4, 'Released'),
        (5, 'Closed'),
    ]

############################################
### For Warehouse Stocks Monitoring
############################################

class AvailableWarehouseStockManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(remaining_stocks__gt=0)

class WarehouseStock(models.Model):
    product = models.ForeignKey(
        "fm.Product", 
        verbose_name=_("Product"), 
        on_delete=models.CASCADE)
    date_received = models.DateField(
        _("Date Received"), 
        auto_now_add=True
    )
    received_by = models.ForeignKey(
        User, 
        verbose_name=_("Received By"), 
        on_delete=models.CASCADE
    )
    supplier_price = models.DecimalField(
        _("Supplier's Price"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    quantity = models.PositiveIntegerField(
        _("Quantity Received"),
        default=0
    )
    remaining_stocks = models.PositiveIntegerField(
        _("Remaining Stocks"),
        default=0
    )
    objects = models.Manager()
    availableStocks = AvailableWarehouseStockManager()

    def __str__(self):
        return self.product.full_description + ": " + str(self.remaining_stocks) + " item(s) left in warehouse."
    

############################################
### For Requisition Vouchers
############################################

class RequisitionVoucher(models.Model):
    requested_by = models.ForeignKey(
        User, 
        related_name='rv_requester',
        on_delete=models.RESTRICT
    )
    requested_at = models.DateTimeField(
        _("Requested at"), 
        auto_now_add=True
    )
    approved_by = models.ForeignKey(
        User, 
        related_name='rv_approver',
        on_delete=models.RESTRICT, 
        null=True,
        default=None
    )
    approved_at = models.DateTimeField(
        _("Approved at"), 
        null=True,
        default=None
    )
    cancelled_by = models.ForeignKey(
        User, 
        related_name='rv_canceller',
        on_delete=models.RESTRICT, 
        null=True,
        default=None
    )
    cancelled_at = models.DateTimeField(
        _("Approved at"), 
        null=True,
        default=None
    )
    process_step = models.PositiveSmallIntegerField(
        _("Process Step"),
        default=1 #Pending
    )


class RV_Product(models.Model):
    rv = models.ForeignKey(RequisitionVoucher, 
        verbose_name=_("Requisition Voucher"), 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "fm.Product", 
        on_delete=models.RESTRICT
    )
    requested_qty = models.PositiveIntegerField(
        _("Requested Quantity"),
        default=0
    )
    released_qty = models.PositiveIntegerField(
        _("Released Quantity"),
        default=0
    )
    received_qty = models.PositiveIntegerField(
        _("Received Quantity"),
        default=0
    )


############################################
### For Store Stocks Monitoring
############################################

class AvailableStoreStockManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(remaining_stocks__gt=0)

class StoreStock(models.Model):
    requisition_voucher = models.ForeignKey(
        RequisitionVoucher,
        verbose_name=_("Source from requisition voucher"),
        on_delete=models.CASCADE
    )
    warehouse_stock = models.ForeignKey(
        WarehouseStock,
        verbose_name=_("Source from warehouse stock"),
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "fm.Product", 
        verbose_name=_("Product"), 
        on_delete=models.CASCADE
    )
    released_by = models.ForeignKey(
        User, 
        related_name='stock_releaser',
        verbose_name=_("Released By"), 
        on_delete=models.CASCADE
    )
    date_received = models.DateField(
        _("Date Received"), 
        auto_now_add=True
    )
    received_by = models.ForeignKey(
        User, 
        related_name='stock_receiver',
        verbose_name=_("Received By"), 
        on_delete=models.CASCADE
    )
    supplier_price = models.DecimalField(
        _("Supplier's Price"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    quantity = models.PositiveIntegerField(
        _("Quantity Received"),
        default=0
    )
    remaining_stocks = models.PositiveIntegerField(
        _("Remaining Stocks"),
        default=0
    )
    objects = models.Manager()
    availableStocks = AvailableStoreStockManager()

    def __str__(self):
        return self.product.full_description + ": " + str(self.remaining_stocks) + " item(s) left in store."
    

class ProductHistory(models.Model):
    product = models.ForeignKey(
        "fm.Product", 
        verbose_name=_("Product"), 
        on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        _("Quantity Received"),
        default=0
    )
    remarks = models.CharField(
        _("Remarks"), 
        max_length=250
    )
    performed_on = models.DateField(
        _("Performed on"), 
        auto_now_add=True
    )
    performed_by = models.ForeignKey(
        User, 
        verbose_name=_("Performed By"), 
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.product.full_description + ": " + str(self.quantity) + " items"
    