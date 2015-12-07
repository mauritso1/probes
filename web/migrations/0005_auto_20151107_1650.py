# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20151107_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probe',
            name='BSSID',
            field=macaddress.fields.MACAddressField(integer=False, max_length=17, verbose_name=b'BSSID'),
        ),
    ]
