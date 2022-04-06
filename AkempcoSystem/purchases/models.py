from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F
from datetime import datetime

from admin_area.models import UserType
from stocks.models import WarehouseStock, ProductHistory

# PO_PROCESS class to monitor the steps in processing documents
class PO_PROCESS:
    STEPS = [
        (1, UserType.PURCHASER), #equivalent to Pending status
        (2, UserType.OIC),
        (3, UserType.AUDIT),
        (4, UserType.GM),
        (5, 'Approved'),
        (6, 'Rejected'),
        (7, 'Cancelled')
    ]

    @staticmethod
    def which_step_this_user_is_in(user):
        for step in PO_PROCESS.STEPS:
            if step[1] == user.userdetail.userType:
                return step[0]
        return 0

    @staticmethod
    def is_po_approver(user):
        step = PO_PROCESS.which_step_this_user_is_in(user)
        return step > 1


# PurchaseOrder model
class PurchaseOrder(models.Model):

    supplier = models.ForeignKey(
        'fm.Supplier',
        verbose_name=_("Supplier"), 
        on_delete=models.RESTRICT,
        null=True,                      # this is equivalent to Cash Purchase
    )
    category = models.ForeignKey(
        'fm.Category',
        verbose_name=_("Category"), 
        on_delete=models.RESTRICT  
    )
    po_date = models.DateField(
        _("PO Date"),        
    )
    notes = models.CharField(
        _("Notes"), 
        max_length=250,
        null=True,
        blank=True,
    )
    po_total = models.DecimalField(
        _("Total Amount"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    parent_po = models.PositiveIntegerField(
        _("Parent PO"),
        help_text="When PO is split for back-order, this is the source PO.",
        null=True,
        default=None
    )
    # approval details
    process_step = models.PositiveSmallIntegerField(
        _("Step"),
        choices=PO_PROCESS.STEPS,
        default=1
    )
    prepared_by = models.ForeignKey(
        User,
        verbose_name=_("Prepared by"), 
        related_name='po_prepared',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None,
    )
    prepared_at = models.DateTimeField(
        _("Prepared at"),
        auto_now_add=True
    )
    oic_checker = models.ForeignKey(
        User,
        verbose_name=_("Officer-In-Charge"), 
        related_name='po_oic_checked',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None,
    )
    oic_checked_at = models.DateTimeField(
        _("Approved by OIC at"),
        null=True,
        blank=True,
        default=None,
    )
    audit_checker = models.ForeignKey(
        User,
        verbose_name=_("Audit Committee"), 
        related_name='po_audit_checked',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None,
    )
    audit_checked_at = models.DateTimeField(
        _("Approved by Audit at"),
        null=True,
        blank=True,
        default=None,
    )
    gm_checker = models.ForeignKey(
        User,
        verbose_name=_("General Manager"), 
        related_name='po_approved',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None,
    )
    gm_checked_at = models.DateTimeField(
        _("Approved by GM at"),
        null=True,
        blank=True,
        default=None,
    )
    # details for rejection
    rejected_by = models.ForeignKey(
        User,
        verbose_name=_("Rejected by"),
        related_name='po_canceller',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None,
    )
    rejected_at = models.DateTimeField(
        _("Rejected at"),
        null=True,
        blank=True,
        default=None,
    )
    reject_reason = models.CharField(
        _("Reason for rejection"),
        max_length=250,
        null=True,
        blank=True,
        default=None
    )
    # details for receiving
    received_date = models.DateField(
        _("Date Received"),
        null=True,
        blank=True,
        default=None,       
    )
    reference_number = models.CharField(
        _("Reference Number"), 
        max_length=250,
        null=True,
        blank=True,
        default=None,
    )
    received_by = models.ForeignKey(
        User,
        verbose_name=_("Received by"), 
        related_name='product_receiver',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None,
    )
    is_open = models.BooleanField(
        verbose_name=_('Is open?'),
        default=True
    )
    is_receiving_now = models.BooleanField(
        verbose_name=_('Is the user receiving stocks now?'),
        default=False
    )
    has_cancelled_items = models.BooleanField(
        verbose_name=_('Is this PO contains cancelled items?'),
        default=False
    )
    # other computed fields
    item_count = models.PositiveIntegerField(
        _("Item Count"),
        default=0
    )
    total_po_amount = models.DecimalField(
        _("Total PO Amount"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    received_item_count = models.PositiveIntegerField(
        _("Received Item Count"),
        default=0
    )
    total_received_amount = models.DecimalField(
        _("Total Received Amount"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        _("Status"), 
        max_length=50,
        default='Pending'
    )

    def __str__(self):
        return "PO # {:08}".format(self.pk)
    
    def update_status(self):
        products = PO_Product.objects.filter(purchase_order=self)
        self.is_open = False
        for prod in products:
            if not prod.is_closed():
                self.is_open = True
                break
            prod.compute_fields()

        self.save()
        self.supplier.fill_in_other_fields()
        # trigger methods that update computed fields
        self.fill_in_other_po_fields()

    def is_for_approval(self, user):
        if self.process_step >= 2 and self.process_step <= 4:
            step = PO_PROCESS.which_step_this_user_is_in(user)
            return self.process_step == step
        else:
            return False

    def fill_in_other_po_fields(self):
        a = self.compute_item_count()
        b = self.compute_total_po_amount()
        c = self.set_status()
        print(f"count={a}, total={b}, status={c}")

    def fill_in_other_received_fields(self):
        self.compute_received_items_count()
        self.compute_total_received_amount()

    def compute_item_count(self):
        val = PO_Product.objects.filter(purchase_order=self).count()
        self.item_count = val
        self.save()
        return val

    def compute_total_po_amount(self):
        val = PO_Product.objects.filter(purchase_order=self).aggregate(total=Sum( F('unit_price') * F('ordered_quantity')))['total']
        self.total_po_amount = val
        self.save()
        return val

    def compute_total_received_amount(self):
        val = PO_Product.objects.filter(purchase_order=self).aggregate(total=Sum( F('unit_price') * F('received_qty')))['total']
        self.total_received_amount = val
        self.save()
        return val

    def compute_received_items_count(self):
        products = PO_Product.objects.filter(purchase_order=self)
        count = 0
        for prod in products:
            if prod.has_received:
                count = count + 1
        self.received_item_count = count
        self.save()
        return count

    def set_status(self):
        if self.is_approved():
            self.status = 'Open' if self.is_open else 'Closed'
        else:
            self.status = self.get_user_step()
        self.save()

    def get_product_ordered(self, product):
        po_prod = PO_Product.objects.filter(purchase_order=self, product=product)
        if po_prod:
            prod = po_prod.first()
            po_prod.delete()
            return prod.ordered_quantity
        else:
            return 0

    def set_supplier_last_po(self):
        self.supplier.last_po = self
        self.supplier.save()

    def submit(self, user):
        self.prepared_by = user
        self.prepared_at = datetime.now()
        self.process_step = 2
        self.save()
        # Supplier fields
        self.set_supplier_last_po()
        self.supplier.fill_in_other_fields()
        # trigger methods that update computed fields
        self.fill_in_other_po_fields()
        # fill out computed fields in PO_Product
        products = PO_Product.objects.filter(purchase_order=self)
        for prod in products:
            prod.compute_fields()

    def approve(self, user):
        # set approver and timestamp
        userType = user.userdetail.userType
        if userType == UserType.OIC:
            self.oic_checker = user
            self.oic_checked_at = datetime.now()

        elif userType == UserType.AUDIT:
            self.audit_checker = user
            self.audit_checked_at = datetime.now()

        elif userType == UserType.GM:
            self.gm_checker = user
            self.gm_checked_at = datetime.now()

        # set next part of process
        step = self.process_step
        self.process_step = step + 1
        self.set_status()
        self.save()

    def reject(self, user, reason):
        self.process_step = 6
        self.rejected_by = user
        self.rejected_at = datetime.now()
        self.reject_reason = reason
        self.save()
        self.set_status()
        self.supplier.fill_in_other_fields()

    def is_checkable(self):
        return (self.process_step > 1 and self.process_step < 5)

    def is_edittable(self):
        return (self.process_step <= 2)

    def get_user_step(self):
        for step in PO_PROCESS.STEPS:
            # return step
            if step[0] == self.process_step:
                if step[0] == 1:
                    return 'Pending'
                elif step[0] > 1 and step[0] < 5:
                    who = ""
                    if step[1] == 'Officer-In-Charge':
                        who = " (" + self.category.category_description + ")"
                    return 'Approval: ' + step[1] + who
                else:
                    return step[1]
        return None

    def get_user_type(self):
        for step in PO_PROCESS.STEPS:
            # return step
            if step[0] == self.process_step:
                return step[1]
        return None

    def is_approved(self):
        return (self.process_step == 5)

    def is_rejected(self):
        return (self.process_step == 6)

    def get_status_css_class(self):
        if self.is_approved() and self.is_open:
            return 'bg-info'
        elif self.process_step == 1:
            return 'text-body'
        elif self.process_step > 1 and self.process_step < 5:
            return 'text-success'
        elif self.process_step == 6:
            return 'text-muted'
        elif self.process_step == 7:
            return 'text-danger'
        else:
            return ''

    def are_all_prices_nonzero(self):
        products = PO_Product.objects.filter(purchase_order=self, unit_price=0).count()
        return products is None or products == 0

    def prepare_for_receiving(self):
        products = PO_Product.objects.filter(purchase_order=self)
        for prod in products:
            prod.receive_now = prod.ordered_quantity - prod.received_qty
            prod.save()

    def receive_stocks(self, user):
        products = PO_Product.objects.filter(purchase_order=self)
        for prod in products:
            # save to warehouse stocks
            print(f"prod.receive_now: {prod.receive_now}")
            if prod.receive_now > 0:
                product = prod.product
                ws = WarehouseStock()
                ws.product = product
                ws.received_by = user
                ws.remaining_stocks = ws.quantity = prod.receive_now
                ws.supplier_price = prod.unit_price
                ws.save()

                # check if this is the only record in WarehouseStock
                count = WarehouseStock.objects.filter(product=product).count()
                # check if the last saved price is different thatn this one
                with_new_price = False
                if count > 0:
                    latest = WarehouseStock.objects.filter(product=product).order_by('-pk').first()
                    with_new_price = latest.supplier_price != prod.unit_price

                # need to trigger price review if this is the first record or there is a price update
                if count == 1 or with_new_price:
                    product.for_price_review = True
                    product.save()
                
                # record history
                hist = ProductHistory()
                hist.product = prod.product
                hist.location = 0
                hist.quantity = prod.receive_now
                hist.remarks = 'Received delivered stocks.'
                hist.performed_by = user
                hist.save()
                
                # update received_qty and clear receive_now
                prod.received_qty = prod.received_qty + prod.receive_now
                prod.receive_now = 0
                prod.save()
                prod.compute_fields()   # required for filling out of computed fields

        self.received_by = user
        self.received_date = datetime.now()
        self.is_receiving_now = False
        self.save()
        self.update_status()
        # trigger methods that update computed fields
        self.compute_received_items_count()
        self.compute_total_received_amount()
        self.supplier.fill_in_other_fields()


    def split_to_backorder(self, child_po):
        products = PO_Product.objects.filter(purchase_order=self)
        for prod in products:
            if prod.undelivered_qty > 0:
                # create new record
                new_prod = PO_Product.objects.get(pk=prod.pk)
                new_prod.pk = None
                new_prod.purchase_order = child_po
                new_prod.ordered_quantity = prod.undelivered_qty
                new_prod.received_qty = 0
                new_prod.receive_now = 0
                new_prod.save()
                new_prod.compute_fields()
                # adjust current record
                prod.ordered_quantity = prod.received_qty
                prod.receive_now = 0
                prod.compute_fields()
                prod.save()

        # update status of each PO (parent closed, child open)
        self.update_status()
        self.fill_in_other_po_fields()
        self.fill_in_other_received_fields()
        child_po.update_status()
        child_po.fill_in_other_po_fields()
        child_po.fill_in_other_received_fields()
        # Supplier fields
        self.supplier.last_po = child_po
        self.supplier.save()

    def cancel_undelivered(self):
        # run over the PO Products, cancelling undelivered items
        products = PO_Product.objects.filter(purchase_order=self)
        for prod in products:
            if prod.received_qty < prod.ordered_quantity:
                # adjust current record
                prod.ordered_quantity = prod.received_qty
                prod.receive_now = 0
                prod.save()

        # close parent PO
        self.update_status()
        self.has_cancelled_items = True
        self.save()
        self.supplier.fill_in_other_fields()

    def clone(self, user):
        new_po = PurchaseOrder.objects.create(
            supplier=self.supplier,
            category=self.category,
            po_date=datetime.now(),
            po_total=self.po_total,
            prepared_by=user 
        )
        new_po.save()

        products = PO_Product.objects.filter(purchase_order=self)
        for p in products:
            p.pk = None
            p.purchase_order = new_po
            p.received_qty = 0
            p.receive_now = False
            p.has_received = False
            p.save()
            p.compute_fields()
            
        new_po.update_status()
        # Supplier fields
        self.supplier.last_po = new_po
        self.supplier.save()

        return new_po

    class Meta:
        ordering = [F('pk').desc(nulls_first=True)]


# PO_Product with One-To-Many relationship with PurchaseOrder
class PO_Product(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'fm.Product',
        verbose_name=_("Product"),
        on_delete=models.RESTRICT
    )
    unit_price = models.DecimalField(
        _("Unit Price"), 
        max_digits=11, 
        decimal_places=2,
        blank=True,
        default=0
    )
    ordered_quantity = models.PositiveIntegerField(
        _("Ordered Quantity")
    )
    received_qty = models.PositiveIntegerField(
        _("Received Quantity"),
        default=0
    )
    receive_now = models.PositiveIntegerField(
        _("Receive Now"),
        default=0
    )
    # other computed fields
    undelivered_qty = models.PositiveIntegerField(
        _("Undelivered Quantity"),
        default=0
    )
    has_received = models.BooleanField(
        _("Has Received?"),
        default=False
    )
    po_subtotal = models.DecimalField(
        _("PO Subtotal"), 
        max_digits=11, 
        decimal_places=2,
        default=0
    )
    received_subtotal = models.DecimalField(
        _("Received Subtotal"), 
        max_digits=11, 
        decimal_places=2,
        default=0 
    )

    def compute_fields(self):
        self.undelivered_qty = self.ordered_quantity - self.received_qty
        self.po_subtotal = self.unit_price * self.ordered_quantity
        self.has_received = (self.received_qty > 0)
        self.received_subtotal = self.unit_price * self.received_qty
        self.save()

    def __str__(self):
        return f"PO# {self.purchase_order.pk}: {self.product.full_description} - {self.ordered_quantity} {self.product.uom.uom_description}"

    def is_closed(self):
        return (self.ordered_quantity == self.received_qty)

    def set_for_price_review(self):
        prod = self.product
        prod.for_price_review = True
        prod.save()


    class Meta:
        ordering = ['-purchase_order', 'product']
        verbose_name = 'PO Product'
        verbose_name_plural = 'PO Products'