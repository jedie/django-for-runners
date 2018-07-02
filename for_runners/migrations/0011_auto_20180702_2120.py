# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-02 21:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('for_runners', '0010_auto_20180628_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gpxmodel',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tracks', to='for_runners.EventModel'),
        ),
    ]