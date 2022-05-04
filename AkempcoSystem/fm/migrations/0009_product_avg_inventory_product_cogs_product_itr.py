# Generated by Django 4.0 on 2022-05-04 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fm', '0008_remove_product_price_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='avg_inventory',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True, verbose_name='Average Inventory'),
        ),
        migrations.AddField(
            model_name='product',
            name='cogs',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True, verbose_name='Cost of Goods Sold'),
        ),
        migrations.AddField(
            model_name='product',
            name='itr',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True, verbose_name='Inventory Turnover Ratio'),
        ),
    ]
