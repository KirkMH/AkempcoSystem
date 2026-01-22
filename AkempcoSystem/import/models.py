from stocks.models import WarehouseStock, StoreStock
from django.db import models
from django.contrib import admin
from django.utils import timezone

from fm.models import Supplier, UnitOfMeasure, Category, Product
from member.models import Creditor


def truncate(s, maxchars):
    '''
    Truncates a string to a maximum number of characters.
    '''
    if s and len(s) > maxchars:
        return s[:maxchars]
    return s or ''

def to_int(value, default=0):
    '''Converts a string to integer, returns default if conversion fails or value is empty/whitespace'''
    if not value or not str(value).strip():
        return default
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return default

def to_float(value, default=0.0):
    '''Converts a string to float, returns default if conversion fails or value is empty/whitespace'''
    if not value or not str(value).strip():
        return default
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return default

IMPORT_TYPES = (
    ('D', 'Data'),
    ('S', 'Supplier'),
    ('C', 'Creditor')
)

TAX_TYPES = (
    ('V', 'VAT'),
    ('E', 'VAT Exempt'),
    ('Z', 'Zero Rated'),
)

class Import(models.Model):
    import_date = models.DateField(auto_now_add=True)
    import_time = models.TimeField(auto_now_add=True)
    import_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    import_type = models.CharField(max_length=1, choices=IMPORT_TYPES)
    import_status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.import_date} {self.import_time}"

    class Meta:
        verbose_name = 'Import'
        verbose_name_plural = 'Imports'
        ordering = ['-import_date', '-import_time']


class ImportItem(models.Model):
    import_ref = models.ForeignKey(Import, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=20)
    full_description = models.CharField(max_length=250)
    short_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    uom = models.CharField(max_length=20)
    reorder_point = models.IntegerField()
    ceiling_qty = models.IntegerField()
    srp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_qty = models.IntegerField()
    tax_type = models.CharField(max_length=1, choices=TAX_TYPES)
    is_prime_commodity = models.BooleanField(default=False)
    is_consigned = models.BooleanField(default=False)
    is_buyer_info_required = models.BooleanField(default=False)
    other_info = models.CharField(max_length=250)
    suppliers = models.CharField(max_length=250)    
    warehouse_qty = models.IntegerField()
    store_qty = models.IntegerField()

    def __str__(self):
        return self.full_description

    def do_import(self, user):
        uom, _ = UnitOfMeasure.objects.get_or_create(
            uom_description=self.uom,
            status='Active'
        )
        category, _ = Category.objects.get_or_create(
            category_description=self.category,
            status='Active'
        )
        supplier_list = []
        if ";" in self.suppliers:
            supplier_list = [s.strip() for s in self.suppliers.split(";") if s.strip()]
        elif "/" in self.suppliers:
            supplier_list = [s.strip() for s in self.suppliers.split("/") if s.strip()]
        else:
            supplier_list = [self.suppliers.strip()] if self.suppliers.strip() else []
        supplier_references = []
        for supplier_name in supplier_list:
            supplier, _ = Supplier.objects.get_or_create(
                supplier_name=truncate(supplier_name, 50),
                status='Active'
            )
            supplier_references.append(supplier)
        from django.db.models import Q
        product = Product.objects.filter(
            Q(barcode=self.barcode) | 
            Q(short_name=self.short_name) | 
            Q(full_description=self.full_description)
        ).first()
        if not product:
            product = Product.objects.create(
                barcode=self.barcode,
                full_description=truncate(self.full_description, 250),
                short_name=truncate(self.short_name, 50),
                category=category,
                uom=uom,
                reorder_point=self.reorder_point,
                ceiling_qty=self.ceiling_qty,
                suggested_retail_price=self.srp,
                selling_price=self.selling_price,
                wholesale_price=self.wholesale_price,
                wholesale_qty=self.wholesale_qty,
                tax_type=self.tax_type,
                for_discount=self.is_prime_commodity,
                is_consignment=self.is_consigned,
                is_buyer_info_needed=self.is_buyer_info_required,
                other_info=self.other_info,
                warehouse_stocks=self.warehouse_qty,
                store_stocks=self.store_qty,
                total_stocks=self.warehouse_qty + self.store_qty,
                created_at=timezone.now(),
                price_updated_on=timezone.now(),
                status='Active'
            )
        WarehouseStock.objects.create(
            product=product,
            received_by=user,
            quantity=self.warehouse_qty,
            remaining_stocks=self.warehouse_qty
        )
        StoreStock.objects.create(
            product=product,
            quantity=self.store_qty,
            remaining_stocks=self.store_qty
        )
        product.suppliers.add(*supplier_references)
        product.save()
        return product

    class Meta:
        verbose_name = 'Import Item'
        verbose_name_plural = 'Import Items'
        ordering = ['-import_ref', 'full_description']


class SupplierItem(models.Model):
    import_ref = models.ForeignKey(Import, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    contact_person = models.CharField(max_length=50)
    contact_info = models.CharField(max_length=20)
    email = models.EmailField()
    tax_type = models.CharField(max_length=1, choices=TAX_TYPES)
    tin = models.CharField(max_length=20)
    deducts_vat = models.BooleanField(default=False)

    def __str__(self):
        return self.supplier_name

    def do_import(self, user):
        supplier = Supplier.objects.filter(
            supplier_name=self.supplier_name,
            address=self.address
        ).first()
        if not supplier:
            TAXTYPE = [
                ("V", "VAT"),
                ("N", "VAT Exempt"),
                ("Z", "Zero Rated")
            ]
            tax_class = next((x for x in TAXTYPE if x[0] == self.tax_type), None)
            supplier = Supplier.objects.create(
                supplier_name=self.supplier_name,
                address=self.address,
                contact_person=self.contact_person,
                contact_info=self.contact_info,
                email=self.email,
                tax_class=tax_class,
                tin=self.tin,
                less_vat=self.deducts_vat,
                created_at=timezone.now(),
                activated_at=timezone.now(),
                status='Active'
            )
        return supplier

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['-import_ref', 'supplier_name']


class CreditorItem(models.Model):
    CREDITOR_TYPES = [
        ('Member', 'Member'),
        ('Group', 'Group Creditor')
    ]

    import_ref = models.ForeignKey(Import, on_delete=models.CASCADE)
    creditor_type = models.CharField(
        max_length=10,
        choices=CREDITOR_TYPES
    )
    id_number = models.CharField(
        max_length=5,
        unique=True,
        null=True, blank=True, default=None
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    tin = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        default=None
    )
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def do_import(self, user):
        creditor = Creditor.objects.filter(
            creditor_type=self.creditor_type,
            id_number=self.id_number,
            name=self.name
        ).first()
        if not creditor:
            creditor = Creditor.objects.create(
                creditor_type=self.creditor_type,
                id_number=self.id_number,
                name=self.name,
                address=self.address,
                tin=self.tin,
                credit_limit=self.credit_limit,
                active=True
            )
        return creditor

    class Meta:
        verbose_name = 'Creditor'
        verbose_name_plural = 'Creditors'
        ordering = ['-import_ref', 'name']
    
    
    

# register to admin
admin.site.register(Import)
admin.site.register(ImportItem)
admin.site.register(SupplierItem)
admin.site.register(CreditorItem)
