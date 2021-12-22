from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# will be used for the status of different models
ACTIVE = 'ACTIVE'
CANCELLED = 'CANCELLED'
STATUS = [
    (ACTIVE, _('Active')),
    (CANCELLED, _('Cancelled'))
]


# UnitOfMeasure model
class UnitOfMeasure(models.Model):
    uom_description = models.CharField(
        _("Unit of measure"), 
        max_length=50, 
        help_text='Use singular form.',
        null=False
    )
    status = models.CharField(
        _("Status"), 
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )

    def __str__(self):
        return self.uom_description

    class Meta:
        ordering = ['uom_description']



# Category model
class Category(models.Model):
    category_description = models.CharField(
        _("Category description"), 
        max_length=50, 
        help_text='Use singular form.',
        null=False
    )
    status = models.CharField(
        _("Status"), 
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )

    def __str__(self):
        return self.category_description

    class Meta:
        ordering = ['category_description']
