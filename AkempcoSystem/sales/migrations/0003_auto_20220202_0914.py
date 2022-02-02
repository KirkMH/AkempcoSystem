# Generated by Django 3.2.7 on 2022-02-02 01:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0002_discount_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sales',
            name='cancelled_by',
        ),
        migrations.RemoveField(
            model_name='sales',
            name='cancelled_on',
        ),
        migrations.RemoveField(
            model_name='sales',
            name='last_reprint',
        ),
        migrations.RemoveField(
            model_name='sales',
            name='reprint_by',
        ),
        migrations.AddField(
            model_name='sales',
            name='status',
            field=models.CharField(choices=[('WIP', 'Work-in-Progress'), ('On-Hold', 'On-Hold'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='WIP', max_length=10, verbose_name='Status'),
        ),
        migrations.CreateModel(
            name='SalesInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sales_datetime', models.DateTimeField(auto_now_add=True, verbose_name='SI Date/Time')),
                ('last_reprint', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last Reprint')),
                ('cancelled_on', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Cancelled on')),
                ('cancelled_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cancelled_by', to=settings.AUTH_USER_MODEL, verbose_name='Cancelled by')),
                ('reprint_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reprinted_by', to=settings.AUTH_USER_MODEL, verbose_name='Reprinted by')),
                ('sales', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sales.sales', verbose_name='Sales Record')),
            ],
            options={
                'ordering': ['-pk'],
            },
        ),
    ]
