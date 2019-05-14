# Generated by Django 2.2.1 on 2019-05-07 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0008_auto_20190504_1925'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='usb',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='wifi',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='features',
            field=models.ManyToManyField(blank=True, to='vehicles.VehicleFeature'),
        ),
    ]