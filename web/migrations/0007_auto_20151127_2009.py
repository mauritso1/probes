# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_probe_router_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(verbose_name=b'Timestamp')),
                ('source_address', macaddress.fields.MACAddressField(integer=False, max_length=17, verbose_name=b'Source address')),
                ('x', models.IntegerField(verbose_name=b'x-coordinate')),
                ('y', models.IntegerField(verbose_name=b'y-coordinate')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='probe',
            unique_together=set([('time', 'source_address')]),
        ),
    ]
