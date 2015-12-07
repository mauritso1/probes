# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_auto_20151128_1252'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='deviceinfo',
            unique_together=set([('identity', 'mac_address')]),
        ),
    ]
