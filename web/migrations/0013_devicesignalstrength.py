# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_auto_20151204_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceSignalStrength',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(verbose_name=b'Timestamp')),
                ('mac_address', macaddress.fields.MACAddressField(integer=False, max_length=17, verbose_name=b'Mac address')),
                ('signal_strength_hg655d', models.IntegerField(verbose_name=b'Signal strength', validators=[django.core.validators.MinValueValidator(-100), django.core.validators.MaxValueValidator(0)])),
                ('signal_strength_710nr', models.IntegerField(verbose_name=b'Signal strength', validators=[django.core.validators.MinValueValidator(-100), django.core.validators.MaxValueValidator(0)])),
                ('signal_strength_710nm', models.IntegerField(verbose_name=b'Signal strength', validators=[django.core.validators.MinValueValidator(-100), django.core.validators.MaxValueValidator(0)])),
            ],
        ),
    ]
