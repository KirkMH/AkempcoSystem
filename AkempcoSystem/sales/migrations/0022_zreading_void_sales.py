# Generated by Django 4.0 on 2022-03-09 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0021_alter_salesitem_less_discount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='zreading',
            name='void_sales',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Beginning Balance'),
            preserve_default=False,
        ),
    ]