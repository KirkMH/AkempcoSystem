# Generated by Django 4.0 on 2022-05-31 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_area', '0008_alter_userdetail_features'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdetail',
            name='userType',
            field=models.CharField(choices=[('Member/Creditor', 'Member/Creditor'), ('Warehouse Staff', 'Warehouse Staff'), ('Sales Personnel', 'Sales Personnel'), ('Storekeeper', 'Storekeeper'), ('Purchaser', 'Purchaser'), ('Officer-In-Charge', 'Officer-In-Charge'), ('Audit Committee', 'Audit Committee'), ('General Manager', 'General Manager'), ('Administrator', 'Administrator')], max_length=20),
        ),
    ]
