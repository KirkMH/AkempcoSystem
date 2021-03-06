# Generated by Django 4.0 on 2022-04-13 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0024_alter_sales_customer_delete_creditor'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='change',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Change Amount'),
        ),
        migrations.AddField(
            model_name='sales',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Discount'),
        ),
        migrations.AddField(
            model_name='sales',
            name='item_count',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Item Count'),
        ),
        migrations.AddField(
            model_name='sales',
            name='less_discount_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Less Discount Total'),
        ),
        migrations.AddField(
            model_name='sales',
            name='less_vat_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Less VAT Total'),
        ),
        migrations.AddField(
            model_name='sales',
            name='payable',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Payable'),
        ),
        migrations.AddField(
            model_name='sales',
            name='sales_without_vat',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Sales Without VAT'),
        ),
        migrations.AddField(
            model_name='sales',
            name='tendered',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Tendered Amount'),
        ),
        migrations.AddField(
            model_name='sales',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Grand Total, disregarding discounts'),
        ),
        migrations.AddField(
            model_name='sales',
            name='vat',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='VAT'),
        ),
        migrations.AddField(
            model_name='sales',
            name='vat_exempt',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='VAT Exempt'),
        ),
        migrations.AddField(
            model_name='sales',
            name='vatable',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Vatable'),
        ),
        migrations.AddField(
            model_name='sales',
            name='with_discount_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Grand Total, considering discounts'),
        ),
        migrations.AddField(
            model_name='sales',
            name='zero_rated',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Zero Rated'),
        ),
        migrations.AddField(
            model_name='salesitem',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Total'),
        ),
        migrations.AddField(
            model_name='salesitem',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Total'),
        ),
        migrations.AddField(
            model_name='xreading',
            name='gross_sales',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Gross Sales'),
        ),
        migrations.AddField(
            model_name='xreading',
            name='total_sales',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Total Sales'),
        ),
        migrations.AddField(
            model_name='xreading',
            name='vd_total_sales',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='VAT Detail Total'),
        ),
    ]
