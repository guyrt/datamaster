# Generated by Django 2.2.8 on 2019-12-20 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('syncer', '0002_auto_20191218_0315'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientDataSetFact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('key', models.CharField(max_length=256)),
                ('value', models.TextField()),
                ('clientdataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='syncer.ClientDataSet')),
            ],
        ),
        migrations.AddConstraint(
            model_name='clientdatasetfact',
            constraint=models.UniqueConstraint(fields=('clientdataset', 'key'), name='ClientDataSetKey'),
        ),
    ]