# Generated by Django 4.1.2 on 2024-01-26 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0052_problem_allowed_languages'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='difficulty',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
