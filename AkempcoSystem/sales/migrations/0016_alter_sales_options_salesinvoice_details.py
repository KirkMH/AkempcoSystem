# Generated by Django 4.0 on 2022-03-03 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0015_remove_salesitemcogs_cogs_salesitemcogs_store_stock'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sales',
            options={'ordering': ['-pk'], 'verbose_name': 'Sales', 'verbose_name_plural': 'Sales'},
        ),
        migrations.AddField(
            model_name='salesinvoice',
            name='details',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Details'),
        ),
    ]
