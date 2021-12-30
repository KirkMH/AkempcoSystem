# Generated by Django 4.0 on 2021-12-30 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fm', '0008_delete_productpricing'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequisitionVoucher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_at', models.DateTimeField(auto_now_add=True, verbose_name='Requested at')),
                ('approved_at', models.DateTimeField(default=None, null=True, verbose_name='Approved at')),
                ('cancelled_at', models.DateTimeField(default=None, null=True, verbose_name='Approved at')),
                ('process_step', models.PositiveSmallIntegerField(default=1, verbose_name='Process Step')),
                ('approved_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='rv_approver', to='auth.user')),
                ('cancelled_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='rv_canceller', to='auth.user')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='rv_requester', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='WarehouseStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_received', models.DateField(auto_now_add=True, verbose_name='Date Received')),
                ('supplier_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Supplier's Price")),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Quantity Received')),
                ('remaining_stocks', models.PositiveIntegerField(default=0, verbose_name='Remaining Stocks')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fm.product', verbose_name='Product')),
                ('received_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='Received By')),
            ],
        ),
        migrations.CreateModel(
            name='StoreStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_received', models.DateField(auto_now_add=True, verbose_name='Date Received')),
                ('supplier_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Supplier's Price")),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Quantity Received')),
                ('remaining_stocks', models.PositiveIntegerField(default=0, verbose_name='Remaining Stocks')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fm.product', verbose_name='Product')),
                ('received_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_receiver', to='auth.user', verbose_name='Received By')),
                ('released_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_releaser', to='auth.user', verbose_name='Released By')),
                ('requisition_voucher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.requisitionvoucher', verbose_name='Source from requisition voucher')),
                ('warehouse_stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.warehousestock', verbose_name='Source from warehouse stock')),
            ],
        ),
        migrations.CreateModel(
            name='RV_Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_qty', models.PositiveIntegerField(default=0, verbose_name='Requested Quantity')),
                ('released_qty', models.PositiveIntegerField(default=0, verbose_name='Released Quantity')),
                ('received_qty', models.PositiveIntegerField(default=0, verbose_name='Received Quantity')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='fm.product')),
                ('rv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.requisitionvoucher', verbose_name='Requisition Voucher')),
            ],
        ),
        migrations.CreateModel(
            name='ProductHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Quantity Received')),
                ('remarks', models.CharField(max_length=250, verbose_name='Remarks')),
                ('performed_on', models.DateField(auto_now_add=True, verbose_name='Performed on')),
                ('performed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='Performed By')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fm.product', verbose_name='Product')),
            ],
        ),
    ]
