# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-09 07:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('url', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('text', models.TextField()),
                ('source', models.CharField(max_length=256)),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
