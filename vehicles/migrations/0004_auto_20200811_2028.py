# Generated by Django 3.1 on 2020-08-11 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0003_auto_20200711_2306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicleedit',
            name='changes',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
