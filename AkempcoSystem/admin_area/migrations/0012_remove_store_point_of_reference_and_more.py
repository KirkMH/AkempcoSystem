# Generated by Django 4.0 on 2023-12-24 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_area', '0011_store_wholesale_markup_below_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='point_of_reference',
        ),
        migrations.AddField(
            model_name='store',
            name='retail_point_of_reference',
            field=models.DecimalField(decimal_places=2, default=0, help_text='The price that will be used as basis for markup computation of retail price. In pesos.', max_digits=5, verbose_name="Retail Price's Point of Reference "),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='store',
            name='wholesale_point_of_reference',
            field=models.DecimalField(decimal_places=2, default=0, help_text='The price that will be used as basis for markup computation of wholesale price. In pesos.', max_digits=5, verbose_name="Wholesale Price's Point of Reference "),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='store',
            name='retail_markup',
            field=models.DecimalField(decimal_places=2, help_text='The retail markup to be applied above the point of reference. In percent, 1-100.', max_digits=5, verbose_name='Retail Markup Above Point of Reference'),
        ),
        migrations.AlterField(
            model_name='store',
            name='retail_markup_below',
            field=models.DecimalField(decimal_places=2, help_text='The retail markup to be applied from the point of reference and below. In percent, 1-100.', max_digits=5, verbose_name='Retail Markup Up To Point of Reference'),
        ),
        migrations.AlterField(
            model_name='store',
            name='wholesale_markup',
            field=models.DecimalField(decimal_places=2, help_text='The wholesale markup to be applied above the point of reference. In percent, 1-100.', max_digits=5, verbose_name='Wholesale Markup Above Point of Reference'),
        ),
        migrations.AlterField(
            model_name='store',
            name='wholesale_markup_below',
            field=models.DecimalField(decimal_places=2, help_text='The wholesale markup to be applied from the point of reference and below. In percent, 1-100.', max_digits=5, verbose_name='Wholesale Markup Up To Point of Reference'),
        ),
    ]
