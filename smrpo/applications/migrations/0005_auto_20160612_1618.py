# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-12 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0004_auto_20160609_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultscourse',
            name='points_result_on_matura',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resultscourse',
            name='points_success_course_3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resultscourse',
            name='points_success_course_4',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resultsmatura',
            name='points_general_success',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resultsmatura',
            name='points_matura',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
