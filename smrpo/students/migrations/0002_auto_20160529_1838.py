# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-29 16:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='emso',
            field=models.CharField(blank=True, max_length=45),
        ),
    ]
