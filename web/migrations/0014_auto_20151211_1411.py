# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_devicesignalstrength'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='devicesignalstrength',
            unique_together=set([('time', 'mac_address')]),
        ),
    ]
