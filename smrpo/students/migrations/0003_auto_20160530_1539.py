# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-30 13:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_auto_20160529_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]
