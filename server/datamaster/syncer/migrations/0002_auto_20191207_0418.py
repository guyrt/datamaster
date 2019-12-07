# Generated by Django 2.2.7 on 2019-12-07 04:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syncer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='clientdataset',
            name='rowlevelunique',
        ),
        migrations.AddField(
            model_name='clientdataset',
            name='local_machine_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 7, 4, 18, 2, 30616)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clientdataset',
            name='metaargs_guid',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='clientdataset',
            name='project',
            field=models.CharField(blank=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name='clientdataset',
            name='timepath',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddConstraint(
            model_name='clientdataset',
            constraint=models.UniqueConstraint(fields=('team', 'user', 'metaargs_guid', 'timepath', 'name', 'project'), name='rowlevelunique'),
        ),
    ]