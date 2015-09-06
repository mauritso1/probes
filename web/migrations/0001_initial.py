# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Probe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mac_address', macaddress.fields.MACAddressField(integer=True, null=True, verbose_name=b'Mac address', blank=True)),
                ('signal_strength', models.IntegerField(verbose_name=b'Signal strength', validators=[django.core.validators.MinValueValidator(-100), django.core.validators.MaxValueValidator(0)])),
                ('channel', models.IntegerField(verbose_name=b'Channel', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('time', models.DateTimeField(verbose_name=b'Timestamp')),
            ],
        ),
    ]
