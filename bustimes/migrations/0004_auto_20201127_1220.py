# Generated by Django 3.1.3 on 2020-11-27 12:20

import bustimes.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bustimes', '0003_auto_20201027_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='stoptime',
            name='pick_up',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='stoptime',
            name='set_down',
            field=models.BooleanField(default=True),
        ),
        migrations.RunSQL(
            """
                ALTER TABLE "bustimes_stoptime" ALTER COLUMN "arrival" TYPE integer USING EXTRACT(EPOCH FROM "arrival"), ALTER COLUMN "arrival" DROP NOT NULL;
                ALTER TABLE "bustimes_stoptime" ALTER COLUMN "departure" TYPE integer USING EXTRACT(EPOCH FROM "departure"), ALTER COLUMN "departure" DROP NOT NULL;
                ALTER TABLE "bustimes_trip" ALTER COLUMN "end" TYPE integer USING EXTRACT(EPOCH FROM "end");
                ALTER TABLE "bustimes_trip" ALTER COLUMN "start" TYPE integer USING EXTRACT(EPOCH FROM "start");
            """,
            state_operations=[
                migrations.AlterField(
                    model_name='stoptime',
                    name='arrival',
                    field=bustimes.fields.SecondsField(blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name='stoptime',
                    name='departure',
                    field=bustimes.fields.SecondsField(blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name='trip',
                    name='end',
                    field=bustimes.fields.SecondsField(),
                ),
                migrations.AlterField(
                    model_name='trip',
                    name='start',
                    field=bustimes.fields.SecondsField(),
                ),
            ]
        )
    ]