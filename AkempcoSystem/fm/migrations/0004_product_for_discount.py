# Generated by Django 4.0 on 2022-02-17 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fm', '0003_alter_product_tax_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='for_discount',
            field=models.BooleanField(default=False, help_text='Is this a basic necessity or prime commodity? SC and PWD discounts will be applied.', verbose_name='Basic necessity or prime commodity?'),
        ),
    ]
