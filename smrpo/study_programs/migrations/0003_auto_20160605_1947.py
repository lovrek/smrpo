# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-05 17:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study_programs', '0002_auto_20160604_1722'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studyprogram',
            options={'ordering': ('name',)},
        ),
    ]