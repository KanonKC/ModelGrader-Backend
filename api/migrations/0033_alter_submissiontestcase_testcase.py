# Generated by Django 4.1.2 on 2023-12-10 03:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_submission_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissiontestcase',
            name='testcase',
            field=models.ForeignKey(db_column='testcase_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.testcase'),
        ),
    ]
