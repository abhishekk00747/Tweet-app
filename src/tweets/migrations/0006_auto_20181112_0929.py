# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-11-12 09:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0005_auto_20181105_0902'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tweet',
            options={'ordering': ['-timestamp']},
        ),
    ]
