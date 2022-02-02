# Generated by Django 4.0 on 2022-01-20 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('fm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_discovered', models.DateField(verbose_name='Date Discovered')),
                ('in_warehouse', models.BooleanField(default=True, help_text="True if BO is in the warehouse, otherwise it's in the store.", verbose_name='Is this in the warehouse?')),
                ('date_reported', models.DateField(auto_now=True, verbose_name='Date Reported')),
                ('date_approved', models.DateField(default=None, null=True, verbose_name='Date Approved')),
                ('date_rejected', models.DateField(default=None, null=True, verbose_name='Date Cancelled')),
                ('reject_reason', models.CharField(default=None, max_length=250, null=True, verbose_name='Reject reason')),
                ('action_taken', models.CharField(default=None, max_length=100, null=True, verbose_name='Action Taken')),
                ('process_step', models.PositiveSmallIntegerField(default=1, verbose_name='Process Step')),
                ('approved_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='bo_approver', to='auth.user', verbose_name='Approved By')),
                ('rejected_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='bo_canceller', to='auth.user', verbose_name='Cancelled By')),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='bo_reporter', to='auth.user', verbose_name='Reported By')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fm.supplier', verbose_name='Supplier')),
            ],
            options={
                'ordering': ['supplier', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='BadOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(verbose_name='Quantity')),
                ('unit_price', models.DecimalField(decimal_places=2, default=None, max_digits=8, null=True, verbose_name='Average Unit Price')),
                ('reason', models.CharField(max_length=100, verbose_name='Reason')),
                ('bad_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bo_items', to='badorder.badorder', verbose_name='Bad Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fm.product', verbose_name='Product')),
            ],
        ),
    ]