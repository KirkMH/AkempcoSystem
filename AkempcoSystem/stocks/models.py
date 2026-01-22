from django.db import models
from django.contrib.auth.models import User
from admin_area.models import UserType
from django.utils.translation import gettext_lazy as _
from django.db.models import F, Sum
from datetime import datetime


# RV_PROCESS class to monitor the steps in processing documents
class RV_PROCESS:
    STEPS = [
        (1, 'Pending'),
        (2, 'For Approval'),
        (3, 'Approved'),
        (4, 'Released'),
        (5, 'Closed'),
        (6, 'Rejected'),
    ]

############################################
# For Warehouse Stocks Monitoring
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
# For Requisition Vouchers
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
    released_by = models.ForeignKey(
        User,
        related_name='rv_releaser',
        on_delete=models.RESTRICT,
        null=True,
        default=None
    )
    released_at = models.DateTimeField(
        _("Released at"),
        null=True,
        default=None
    )
    received_by = models.ForeignKey(
        User,
        related_name='rv_receiver',
        on_delete=models.RESTRICT,
        null=True,
        default=None
    )
    received_at = models.DateTimeField(
        _("Received at"),
        null=True,
        default=None
    )
    rejected_by = models.ForeignKey(
        User,
        related_name='rv_rejecter',
        on_delete=models.RESTRICT,
        null=True,
        default=None
    )
    rejected_at = models.DateTimeField(
        _("Rejected at"),
        null=True,
        default=None
    )
    reject_reason = models.CharField(
        _("Reject Reason"),
        max_length=250,
        null=True,
        default=None
    )
    process_step = models.PositiveSmallIntegerField(
        _("Process Step"),
        default=1  # Pending
    )
    item_count = models.PositiveIntegerField(
        _("Item Count"),
        default=0
    )
    status = models.CharField(
        _("Status"),
        max_length=15,
        default=RV_PROCESS.STEPS[0][1]
    )

    def __str__(self):
        return 'RV# ' + str(self.pk) + ': ' + self.status

    def set_item_count(self):
        count = RV_Product.objects.filter(rv=self).count() or 0
        self.item_count = count
        self.save()

    def set_status(self):
        status = None
        for step in RV_PROCESS.STEPS:
            if self.process_step == step[0]:
                status = step[1]
        self.status = status
        self.save()

    def is_pending(self):
        return self.process_step == 1

    def is_processed(self):
        return self.process_step > 2

    def is_submitted(self):
        return self.process_step == 2

    def is_approved(self):
        return self.process_step == 3

    def is_released(self):
        return self.process_step == 4

    def is_closed(self):
        return self.process_step == 5

    def is_rejected(self):
        return self.process_step == 6

    def is_open(self):
        return self.process_step > 1 and self.process_step < 5

    def submit(self):
        self.process_step = 2
        self.save()
        self.set_item_count()
        self.set_status()

    def approve(self, user):
        self.approved_by = user
        self.approved_at = datetime.now()
        self.process_step = 3
        self.save()
        self.set_status()

    def release(self, user):
        self.released_by = user
        self.released_at = datetime.now()
        self.process_step = 4
        self.save()
        self.set_status()

    def move_to_store(self, user, whs_pk, qty):
        whs = WarehouseStock.objects.get(pk=whs_pk)
        # deduct qty from wh's remaining stocks
        whs.remaining_stocks = whs.remaining_stocks - qty
        whs.save()
        # create a new store record
        ss = StoreStock()
        ss.requisition_voucher = self
        ss.warehouse_stock = whs
        ss.product = whs.product
        ss.supplier_price = whs.supplier_price
        ss.quantity = qty
        ss.remaining_stocks = qty
        ss.save()

    def receive(self, user):
        self.received_by = user
        self.received_at = datetime.now()
        self.process_step = 5
        self.set_status()
        self.save()
        # get list of requested products
        reqs = RV_Product.objects.filter(rv=self)
        for r in reqs:
            # get WH stocks of this product
            whs = WarehouseStock.availableStocks.filter(
                product=r.product).order_by('pk')
            qty = int(r.quantity)
            for wh in whs:
                stocks = int(wh.remaining_stocks)
                if qty <= stocks:
                    # this record has sufficient stocks; transfer entire qty
                    self.move_to_store(user, wh.pk, qty)
                    qty = 0
                    break
                else:
                    # this record has insufficient stocks
                    # compute remaining qty to transfer from the next record
                    qty = qty - stocks
                    # transfer only the remaining_stocks of this record
                    self.move_to_store(user, wh.pk, stocks)

            # record in history
            hist = ProductHistory()
            hist.product = r.product
            hist.location = 0  # warehouse
            hist.quantity = 0 - r.quantity
            hist.remarks = 'Transfered to the store.'
            hist.performed_by = self.released_by
            hist.save()
            hist.set_current_balance()
            # record in history
            hist.pk = None
            hist.location = 1  # store
            hist.quantity = r.quantity
            hist.remarks = 'Received from the warehouse.'
            hist.save()
            hist.set_current_balance()
            # update product stocks
            r.product.set_stock_count()  # update product stocks

    def reject(self, user, reason):
        self.rejected_by = user
        self.rejected_at = datetime.now()
        self.process_step = 6
        self.set_status()
        self.save()

    def clone(self, user):
        new_rv = RequisitionVoucher.objects.create(
            requested_by=user,
            process_step=1,
            status='Pending'
        )
        new_rv.save()
        products = RV_Product.objects.filter(rv=self)
        for p in products:
            p.pk = None
            p.rv = new_rv
            p.save()
        return new_rv

    def get_product_requested(self, product):
        rv_prod = RV_Product.objects.filter(rv=self, product=product)
        if rv_prod:
            prod = rv_prod.first()
            rv_prod.delete()
            return prod.quantity
        else:
            return 0

    class Meta:
        ordering = [F('pk').desc(nulls_first=True)]


class RV_Product(models.Model):
    rv = models.ForeignKey(RequisitionVoucher,
                           verbose_name=_("Requisition Voucher"),
                           on_delete=models.CASCADE
                           )
    product = models.ForeignKey(
        "fm.Product",
        on_delete=models.RESTRICT
    )
    quantity = models.PositiveIntegerField(
        _("Quantity"),
        default=0
    )

    def __str__(self):
        return f"{self.quantity} {self.product.uom}(s) of {self.product.full_description}"

    class Meta:
        ordering = ['product']


############################################
# For Store Stocks Monitoring
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


class ProducHistoryManagerForWarehouse(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(location=0)  # 0=Warehouse


class ProducHistoryManagerForStore(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(location=1)  # 1=Store


class ProductHistory(models.Model):
    product = models.ForeignKey(
        "fm.Product",
        verbose_name=_("Product"),
        on_delete=models.CASCADE
    )
    location = models.PositiveSmallIntegerField(
        _("Location where the transaction happened. 0=Warehouse; 1=Store")
    )
    quantity = models.IntegerField(
        _("Quantity"),
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
    balance = models.IntegerField(
        _("Current Balance"),
        default=0
    )
    objects = models.Manager()
    for_warehouse = ProducHistoryManagerForWarehouse()
    for_store = ProducHistoryManagerForStore()

    class Meta:
        ordering = ['-performed_on', 'product']
        verbose_name_plural = 'Product History'

    def __str__(self):
        return 'Product: ' + self.product.full_description + '\n' + \
            'Location: ' + 'Warehouse' if self.location == 0 else 'Store' + '\n' + \
            'Quantity: ' + str(self.quantity) + '\n' + \
            'Remarks: ' + self.remarks + '\n'

    def set_current_balance(self):
        last_entry = ProductHistory.objects.filter(
            product=self.product,
            location=self.location,
            pk__lt=self.pk
        ).order_by('-pk')[:1]

        last_bal = 0
        if last_entry:
            last_entry = last_entry.first()
            last_bal = last_entry.balance
        self.balance = last_bal + self.quantity
        self.save()
        self.product.set_stock_count()


class StockAdjustment(models.Model):
    location_options = [
        (0, 'Warehouse'),
        (1, 'Store')
    ]

    product = models.ForeignKey(
        "fm.Product",
        help_text=_("Product to adjust"),
        verbose_name=_("Product"),
        on_delete=models.CASCADE
    )
    quantity = models.SmallIntegerField(
        _("By how many?"),
        help_text="Negative to reduce the quantity, positive to increase the quantity."
    )
    location = models.PositiveSmallIntegerField(
        _("Location"),
        help_text="Where will the adjustment be made?",
        choices=location_options
    )
    reason = models.CharField(_("Reason for adjustment"), max_length=250)
    created_by = models.ForeignKey(
        User,
        related_name='adjustment_requester',
        on_delete=models.RESTRICT
    )
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True
    )
    checked_by = models.ForeignKey(
        User,
        related_name='adjustment_checker',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None
    )
    checked_at = models.DateTimeField(
        _("Checked at"),
        null=True,
        blank=True,
        default=None
    )
    approved_by = models.ForeignKey(
        User,
        related_name='adjustment_approver',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None
    )
    approved_at = models.DateTimeField(
        _("Approved at"),
        null=True,
        blank=True,
        default=None
    )
    performed_by = models.ForeignKey(
        User,
        related_name='adjustment_performer',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None
    )
    performed_at = models.DateTimeField(
        _("Performed at"),
        null=True,
        blank=True,
        default=None
    )
    cancelled_by = models.ForeignKey(
        User,
        related_name='adjustment_canceller',
        on_delete=models.RESTRICT,
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
    status = models.CharField(
        _("Status"),
        max_length=10,
        default='Submitted'
    )

    class Meta:
        ordering = ['-created_at', 'product']

    def __str__(self):
        return self.product.full_description + ": " + str(self.quantity) + " due to " + self.reason

    @property
    def location_str(self):
        return 'Warehouse' if self.location == 0 else 'Store'

    @property
    def is_completed(self):
        return self.status == 'Completed'

    @property
    def is_cancelled(self):
        return self.status == 'Cancelled'

    def next_to_approve(self):
        if self.checked_by == None:
            return UserType.AUDIT
        elif self.approved_by == None:
            return UserType.GM
        elif self.performed_by == None:
            return UserType.ADMIN
        else:
            return None

    def cancel(self, user):
        if self.is_completed:
            return

        self.cancelled_by = user
        self.cancelled_at = datetime.now()
        self.status = 'Cancelled'
        self.save()

    def approve(self, user):
        if user.userdetail.userType == UserType.AUDIT:
            self.checked_by = user
            self.checked_at = datetime.now()
            self.status = 'Checked'
        elif user.userdetail.userType == UserType.GM:
            self.approved_by = user
            self.approved_at = datetime.now()
            self.status = 'Approved'
        self.save()

    def perform(self, user):
        # if already completed, ignore action
        if self.is_completed:
            return

        # increase/decrease quantity and log to product history

        # get stocks of this product
        source = WarehouseStock if self.location == 0 else StoreStock
        stock_source = source.availableStocks.filter(
            product=self.product).order_by('pk')
        qty = self.quantity

        if qty > 0:
            # add qty to stocks
            if stock_source:
                stock = stock_source.first()
            else:
                stock = source.objects.filter(
                    product=self.product).order_by('-pk').first()
            if stock:
                stock.remaining_stocks = stock.remaining_stocks + qty
                stock.save()

        else:
            # deduct qty from stock
            qty = abs(qty)
            for item in stock_source:
                stocks = int(item.remaining_stocks)
                if qty <= stocks:
                    # this record has sufficient stocks; deduct entire qty
                    item.remaining_stocks = item.remaining_stocks - qty
                    item.save()
                    qty = 0
                    break
                else:
                    # this record has insufficient stocks
                    # compute remaining qty to transfer from the next record
                    qty = qty - stocks
                    # transfer only the remaining_stocks of this record
                    item.remaining_stocks = 0
                    item.save()

        # record in history
        hist = ProductHistory()
        hist.product = self.product
        hist.location = self.location
        hist.quantity = self.quantity
        hist.remarks = 'Stock adjustment: ' + self.reason
        hist.performed_by = self.created_by
        hist.save()
        hist.set_current_balance()

        # update status
        self.performed_by = user
        self.performed_at = datetime.now()
        self.status = 'Completed'
        self.save()
