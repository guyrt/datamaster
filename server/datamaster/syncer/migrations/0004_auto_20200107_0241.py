# Generated by Django 2.2.8 on 2020-01-07 02:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('syncer', '0003_auto_20191220_2057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientdataset',
            name='local_machine_name',
        ),
        migrations.RemoveField(
            model_name='clientdataset',
            name='local_machine_time',
        ),
        migrations.RemoveField(
            model_name='clientdataset',
            name='local_path',
        ),
        migrations.AlterField(
            model_name='clientdatasetfact',
            name='clientdataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='facts', to='syncer.ClientDataSet'),
        ),
    ]
