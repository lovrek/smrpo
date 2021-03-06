# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-12 16:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0005_auto_20160612_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultscourse',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='information.Course', verbose_name='Ime predmeta'),
        ),
        migrations.AlterField(
            model_name='resultscourse',
            name='passed',
            field=models.BooleanField(verbose_name='Opravil predmet'),
        ),
        migrations.AlterField(
            model_name='resultscourse',
            name='result_on_matura',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ocena na maturi'),
        ),
        migrations.AlterField(
            model_name='resultscourse',
            name='success_course_3',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ocena v 3. letniku'),
        ),
        migrations.AlterField(
            model_name='resultscourse',
            name='success_course_4',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ocena v 4. letniku'),
        ),
        migrations.AlterField(
            model_name='resultsmatura',
            name='general_success_3',
            field=models.IntegerField(blank=True, null=True, verbose_name='Končni uspeh v 3. letniku'),
        ),
        migrations.AlterField(
            model_name='resultsmatura',
            name='general_success_4',
            field=models.IntegerField(blank=True, null=True, verbose_name='Končni uspeh v 4. letniku'),
        ),
        migrations.AlterField(
            model_name='resultsmatura',
            name='matura',
            field=models.IntegerField(blank=True, null=True, verbose_name='Število točk na maturi'),
        ),
        migrations.AlterField(
            model_name='resultsmatura',
            name='passed',
            field=models.BooleanField(verbose_name='Opravil maturo'),
        ),
    ]
