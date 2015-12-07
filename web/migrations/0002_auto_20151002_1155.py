# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import macaddress.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='probe',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='probe',
            name='mac_address',
        ),
        migrations.AddField(
            model_name='probe',
            name='BSSID',
            field=macaddress.fields.MACAddressField(integer=True, null=True, verbose_name=b'BSSID', blank=True),
        ),
        migrations.AddField(
            model_name='probe',
            name='destination_address',
            field=macaddress.fields.MACAddressField(integer=True, null=True, verbose_name=b'Destination address', blank=True),
        ),
        migrations.AddField(
            model_name='probe',
            name='frequency',
            field=models.IntegerField(default=2456, verbose_name=b'Signal strength', validators=[django.core.validators.MinValueValidator(2412), django.core.validators.MaxValueValidator(2472)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='probe',
            name='source_address',
            field=macaddress.fields.MACAddressField(integer=True, null=True, verbose_name=b'Source address', blank=True),
        ),
    ]
