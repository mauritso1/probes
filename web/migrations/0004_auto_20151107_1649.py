# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20151002_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probe',
            name='BSSID',
            field=macaddress.fields.MACAddressField(default='64:D1:A3:32:D2:46', integer=True, verbose_name=b'BSSID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='probe',
            name='destination_address',
            field=macaddress.fields.MACAddressField(max_length=17, null=True, verbose_name=b'Destination address', integer=False, blank=True),
        ),
        migrations.AlterField(
            model_name='probe',
            name='source_address',
            field=macaddress.fields.MACAddressField(default='00:1D:7E:BB:DD:4E', integer=False, max_length=17, verbose_name=b'Source address'),
            preserve_default=False,
        ),
    ]
