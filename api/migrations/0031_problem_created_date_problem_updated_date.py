# Generated by Django 4.1.2 on 2023-12-02 17:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_testcase_runtime_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='problem',
            name='updated_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
