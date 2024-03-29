# Generated by Django 4.1.2 on 2023-12-20 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_bestsubmission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='description',
            field=models.CharField(blank=True, default=None, max_length=100000, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='description',
            field=models.CharField(max_length=100000),
        ),
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=models.CharField(blank=True, default=None, max_length=100000, null=True),
        ),
    ]
