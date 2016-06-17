# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-01 21:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('information', '0005_finishededucation'),
        ('students', '0004_auto_20160530_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='profession',
        ),
        migrations.AddField(
            model_name='student',
            name='finished_education',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='information.FinishedEducation'),
        ),
    ]
