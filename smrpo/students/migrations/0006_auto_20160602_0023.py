# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-01 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_auto_20160601_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='application',
            field=models.ManyToManyField(blank=True, through='students.Applications', to='study_programs.StudyProgram'),
        ),
    ]
