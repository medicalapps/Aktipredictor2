# Generated by Django 3.1.2 on 2022-08-28 16:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0002_auto_20220828_1815'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectorsettings',
            name='avrageWindow',
        ),
        migrations.AlterField(
            model_name='collectorsettings',
            name='RSIintervall',
            field=models.IntegerField(default=30),
        ),
        migrations.AlterField(
            model_name='collectorsettings',
            name='ValidStockdataLimit',
            field=models.IntegerField(default=50),
        ),
        migrations.AlterField(
            model_name='collectorsettings',
            name='firstInculdedDate',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 8, 28, 18, 32, 56, 668322)),
        ),
        migrations.AlterField(
            model_name='collectorsettings',
            name='lastIncudedDate',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 8, 28, 18, 32, 56, 668322)),
        ),
    ]
