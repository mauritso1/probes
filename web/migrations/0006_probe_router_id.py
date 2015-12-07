# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20151107_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='probe',
            name='router_id',
            field=models.CharField(default='other', max_length=15, verbose_name=b'Router name', choices=[(b'HG655D', b'Huawei HG655D'), (b'710Nr', b'TL-WR710N Ramon'), (b'710Nm', b'TL-WR710N Maurits'), (b'experiaboxv8', b'Experiabox V8'), (b'other', b'Other')]),
            preserve_default=False,
        ),
    ]
