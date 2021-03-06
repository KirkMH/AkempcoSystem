# Generated by Django 4.0 on 2022-03-24 06:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_area', '0005_alter_userdetail_linked_creditor_acct'),
        ('member', '0001_initial'),
        ('sales', '0023_alter_zreading_xreading'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='customer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='member.creditor', verbose_name='Customer'),
        ),
        migrations.DeleteModel(
            name='Creditor',
        ),
    ]
