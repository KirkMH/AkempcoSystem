# Generated by Django 3.2.7 on 2022-02-02 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_auto_20220202_1554'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sales',
            name='payable',
        ),
        migrations.RemoveField(
            model_name='sales',
            name='total',
        ),
        migrations.RemoveField(
            model_name='sales',
            name='vat',
        ),
        migrations.RemoveField(
            model_name='sales',
            name='vat_exempt',
        ),
        migrations.RemoveField(
            model_name='sales',
            name='vatable',
        ),
        migrations.RemoveField(
            model_name='sales',
            name='zero_rated',
        ),
        migrations.RemoveField(
            model_name='salesitem',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='salesitem',
            name='subtotal',
        ),
        migrations.RemoveField(
            model_name='salesitem',
            name='total',
        ),
    ]
