# Generated by Django 4.0 on 2022-03-09 09:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0022_zreading_void_sales'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zreading',
            name='xreading',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sales.xreading', verbose_name='X-Reading'),
        ),
    ]
