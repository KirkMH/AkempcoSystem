# Generated by Django 3.2.7 on 2021-12-23 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0002_purchaseorder_is_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='parent_po',
            field=models.PositiveIntegerField(default=None, help_text='When PO is split for back-order, this is the source PO.', null=True, verbose_name='Parent PO'),
        ),
    ]