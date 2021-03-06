# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-08 14:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('information', '0006_auto_20160605_1947'),
        ('students', '0008_applications_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='high_school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='information.HighSchool'),
        ),
        migrations.AddField(
            model_name='student',
            name='profession',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='information.Profession'),
        ),
    ]
