# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_auto_20151128_1315'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='probe',
            unique_together=set([('time', 'source_address', 'router_id')]),
        ),
    ]
