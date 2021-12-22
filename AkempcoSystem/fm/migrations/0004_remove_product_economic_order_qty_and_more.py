# Generated by Django 4.0 on 2021-12-22 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fm', '0003_product_productpricing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='economic_order_qty',
        ),
        migrations.AddField(
            model_name='product',
            name='ceiling_qty',
            field=models.PositiveIntegerField(default=50, help_text='The maximum quantity you should keep in inventory in order to meet your demand and avoid overstocking.', verbose_name='Ceiling Quantity'),
        ),
        migrations.AlterField(
            model_name='product',
            name='reorder_point',
            field=models.PositiveIntegerField(default=20, help_text="The level (quantity) when you will need to place an order so you won't run out of stock.", verbose_name='Reorder Point'),
        ),
    ]