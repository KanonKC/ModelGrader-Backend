# Generated by Django 4.1.2 on 2022-11-19 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_account_is_private_problem_is_private_topic_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProblemTopic',
            new_name='TopicProblem',
        ),
    ]
