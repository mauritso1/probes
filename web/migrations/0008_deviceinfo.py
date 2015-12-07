# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20151127_2009'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identity', models.CharField(max_length=20, verbose_name=b'Identity')),
                ('mac_address', macaddress.fields.MACAddressField(integer=False, max_length=17, verbose_name=b'Mac address')),
            ],
        ),
    ]
