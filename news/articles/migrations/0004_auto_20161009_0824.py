# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-09 08:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_auto_20161009_0816'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleview',
            name='read',
            field=models.BooleanField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='articleview',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
