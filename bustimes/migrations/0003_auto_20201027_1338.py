# Generated by Django 3.1.2 on 2020-10-27 13:38

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bustimes', '0002_auto_20200930_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='geometry',
            field=django.contrib.gis.db.models.fields.MultiLineStringField(blank=True, null=True, srid=4326),
        ),
    ]
