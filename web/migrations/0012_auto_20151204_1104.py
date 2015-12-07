# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0011_auto_20151130_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceinfo',
            name='identity',
            field=models.CharField(max_length=100, verbose_name=b'Identity'),
        ),
    ]
