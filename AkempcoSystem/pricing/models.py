from django.db import models
from django.utils.translation import gettext_lazy as _

from fm.models import Product
from django.contrib.auth.models import User


# ProductPricing model, for price monitoring
class ProductPricing(models.Model):
    product = models.ForeignKey(
        Product, 
        verbose_name=_("Product"), 
        on_delete=models.CASCADE
    )
    retail_price = models.DecimalField(
        _("Retail Price"), 
        max_digits=11, 
        decimal_places=2,
        null=True,
        blank=True
    )
    wholesale_price = models.DecimalField(
        _("Wholesale Price"), 
        max_digits=11, 
        decimal_places=2,
        null=True,
        blank=True
    )
    price_updated_on = models.DateField(
        _("Price updated on"),
        null=True,
        default=None 
    )
    price_tagged_by = models.ForeignKey(
        User,
        verbose_name=_("Price tagged by"),
        on_delete=models.RESTRICT
    )