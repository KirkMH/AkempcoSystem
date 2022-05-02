# Generated by Django 4.0 on 2022-04-23 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0026_alter_salesitem_subtotal'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesinvoice',
            name='is_cancelled',
            field=models.BooleanField(default=False, verbose_name='Is Cancelled?'),
        ),
        migrations.AddField(
            model_name='salesinvoice',
            name='payment_modes',
            field=models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='Payment Modes'),
        ),
    ]