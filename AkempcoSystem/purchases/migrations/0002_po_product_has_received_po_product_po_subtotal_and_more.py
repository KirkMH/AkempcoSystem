# Generated by Django 4.0 on 2022-04-04 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='po_product',
            name='has_received',
            field=models.BooleanField(default=False, verbose_name='Has Received?'),
        ),
        migrations.AddField(
            model_name='po_product',
            name='po_subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='PO Subtotal'),
        ),
        migrations.AddField(
            model_name='po_product',
            name='received_subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Received Subtotal'),
        ),
        migrations.AddField(
            model_name='po_product',
            name='undelivered_qty',
            field=models.PositiveIntegerField(default=0, verbose_name='Undelivered Quantity'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='item_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Item Count'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='received_item_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Received Item Count'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='status',
            field=models.CharField(default='Pending', max_length=50, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='total_po_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Total PO Amount'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='total_received_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Total Received Amount'),
        ),
    ]
