# Generated by Django 4.0 on 2022-02-05 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_alter_sales_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesitem',
            name='supplier_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Supplier Price'),
        ),
        migrations.CreateModel(
            name='SalesPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_mode', models.CharField(choices=[('Cash', 'Cash'), ('Cheque', 'Cheque'), ('Charge', 'Charge'), ('Gift Certificate', 'Gift Certificate'), ('E-Money', 'E-Money'), ('Debit/Credit Card', 'Debit/Credit Card')], default='Cash', max_length=20, verbose_name='Payment Mode')),
                ('details', models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='Payment Details')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Amount Tendered')),
                ('sales', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.sales', verbose_name='Sales Record')),
            ],
        ),
    ]
