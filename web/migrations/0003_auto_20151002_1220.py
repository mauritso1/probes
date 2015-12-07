# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20151002_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probe',
            name='frequency',
            field=models.IntegerField(verbose_name=b'Frequency', validators=[django.core.validators.MinValueValidator(2412), django.core.validators.MaxValueValidator(2472)]),
        ),
        migrations.AlterUniqueTogether(
            name='probe',
            unique_together=set([('time', 'source_address', 'signal_strength')]),
        ),
    ]
