# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-04 16:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_auto_20160603_1345'),
        ('information', '0005_finishededucation'),
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultsCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_on_matura', models.IntegerField(blank=True, null=True)),
                ('success_course_3_4', models.FloatField(blank=True, null=True)),
                ('passed', models.BooleanField()),
                ('type_course', models.IntegerField(blank=True, null=True)),
                ('type_course_profession', models.IntegerField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='information.Course')),
            ],
        ),
        migrations.CreateModel(
            name='ResultsMatura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matura', models.IntegerField(blank=True, null=True)),
                ('general_success', models.FloatField(blank=True, null=True)),
                ('passed', models.BooleanField()),
                ('student_type', models.IntegerField(blank=True, null=True)),
                ('student_type_profession', models.IntegerField(blank=True, null=True)),
                ('course', models.ManyToManyField(through='applications.ResultsCourse', to='information.Course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.Student')),
            ],
        ),
        migrations.AlterField(
            model_name='applicationproperty',
            name='open_datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='resultscourse',
            name='matura',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.ResultsMatura'),
        ),
    ]