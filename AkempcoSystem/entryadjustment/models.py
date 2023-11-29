from django.db import models
from django.contrib.auth.models import User
from admin_area.models import UserType
from django.utils.translation import gettext_lazy as _
from datetime import datetime



class EntryAdjustment(models.Model):
    transaction_type = models.CharField(_("Transaction Type"), max_length=50)
    reference_num = models.CharField(_("Reference Number"), max_length=50)
    adjustment_detail = models.TextField(_("Adjustment Detail"))
    reason = models.CharField(_("Reason for adjustment"), max_length=250)
    requested_by = models.ForeignKey(
        User, 
        related_name='entryadj_requester',
        on_delete=models.RESTRICT
    )
    requested_at = models.DateTimeField(
        _("Requested at"), 
        auto_now_add=True
    )
    checked_by = models.ForeignKey(
        User, 
        related_name='entryadj_checker',
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
        related_name='entryadj_approver',
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
        related_name='entryadj_performer',
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
        related_name='entryadj_canceller',
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
        ordering = ['-requested_at', 'transaction_type']

    def __str__(self):
        return self.transaction_type + ": " + self.adjustment_detail

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

        # update status
        self.performed_by = user
        self.performed_at = datetime.now()
        self.status = 'Completed'
        self.save()