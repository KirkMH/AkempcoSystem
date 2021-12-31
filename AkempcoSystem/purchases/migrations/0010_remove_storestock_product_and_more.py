# Generated by Django 4.0 on 2021-12-30 07:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0009_purchaseorder_has_cancelled_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storestock',
            name='product',
        ),
        migrations.RemoveField(
            model_name='storestock',
            name='received_by',
        ),
        migrations.RemoveField(
            model_name='warehousestock',
            name='product',
        ),
        migrations.RemoveField(
            model_name='warehousestock',
            name='received_by',
        ),
        migrations.DeleteModel(
            name='ProductHistory',
        ),
        migrations.DeleteModel(
            name='StoreStock',
        ),
        migrations.DeleteModel(
            name='WarehouseStock',
        ),
    ]