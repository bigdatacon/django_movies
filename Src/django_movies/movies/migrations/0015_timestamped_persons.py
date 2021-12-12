# Generated by Django 3.2.7 on 2021-11-11 14:34

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0014_rename_persons_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='genrefilmwork',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата обращения'),
        ),
        migrations.AlterField(
            model_name='personfilmwork',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата обращения'),
        ),
    ]