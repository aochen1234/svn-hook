# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-11 09:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testappp', '0003_auto_20170711_1746'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testrule',
            name='slug',
        ),
    ]