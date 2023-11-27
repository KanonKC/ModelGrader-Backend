# Generated by Django 4.1.2 on 2023-11-24 05:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_alter_problem_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='is_admin',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='problem',
            name='account',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='account',
        ),
        migrations.AddField(
            model_name='collection',
            name='creator',
            field=models.ForeignKey(db_column='creator_id', default=1, on_delete=django.db.models.deletion.CASCADE, to='api.account'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='problem',
            name='creator',
            field=models.ForeignKey(db_column='creator_id', default=1, on_delete=django.db.models.deletion.CASCADE, to='api.account'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='topic',
            name='creator',
            field=models.ForeignKey(db_column='creator_id', default=1, on_delete=django.db.models.deletion.CASCADE, to='api.account'),
            preserve_default=False,
        ),
    ]