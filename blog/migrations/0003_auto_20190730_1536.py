# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-07-30 15:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20190730_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='theme',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='博客主题'),
        ),
    ]