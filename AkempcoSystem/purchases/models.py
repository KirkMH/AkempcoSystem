from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Coalesce
from django.db.models import F

from admin_area.models import UserType

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


# PurchaseOrder model
class PurchaseOrder(models.Model):

    sequence_number = models.PositiveIntegerField(
        _("Sequence Number"),
        null=True,
        blank=True,
        default=None
    )
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
        null=True,
        blank=True,
        default=None,
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
    )
    reference_number = models.CharField(
        _("Reference Number"), 
        max_length=250,
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

    def __str__(self):
        if self.sequence_number:
            return "PO # {:08}".format(self.sequence_number)
        else:
            return "For " + self.supplier.supplier_name + " on " + self.po_date.strftime("%B %d %Y")
    
    def update_status(self):
        products = PO_Product.objects.get(purchase_order=self)
        for prod in products:
            if not prod.is_closed():
                self.is_open = False
                return None

    def get_item_count(self):
        return PO_Product.objects.filter(purchase_order=self).count()

    def is_checkable(self):
        return (self.process_step > 1 and self.process_step < 5)

    def is_edittable(self):
        return (self.process_step <= 2)

    def get_user_step(self):
        for step in PO_PROCESS.STEPS:
            # return step
            if step[0] == self.process_step:
                if step[0] > 1 and step[0] < 5:
                    return 'Approval: %s' % step[1]
                else:
                    return step[1]
        return None

    def get_status_css_class(self):
        if self.status == 0: # rejected
            return 'bg-danger'
        elif self.status == 5: # approved
            return 'bg-info'
        else:
            return ''

    class Meta:
        ordering = [F('sequence_number').desc(nulls_first=True)]


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

    def __str__(self):
        return self.product.full_description + ": " + str(self.quantity) + " " + self.product.uom.uom_description

    def is_closed(self):
        return (self.quantity == self.received_qty)

    def get_po_subtotal(self):
        return self.unit_price * self.ordered_quantity

    def get_received_subtotal(self):
        return self.unit_price * self.received_quantity

    class Meta:
        ordering = ['product']

