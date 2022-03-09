# Generated by Django 4.0 on 2022-03-09 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0019_salespayment_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salespayment',
            name='value',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Accepted Value'),
        ),
    ]