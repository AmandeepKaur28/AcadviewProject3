# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 05:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_auto_20170722_0020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categorymodel',
            name='tags',
        ),
        migrations.AddField(
            model_name='postmodel',
            name='tags',
            field=models.CharField(default=2, max_length=100),
            preserve_default=False,
        ),
    ]
