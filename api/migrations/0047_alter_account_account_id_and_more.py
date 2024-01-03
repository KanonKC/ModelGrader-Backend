# Generated by Django 4.1.2 on 2023-12-31 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0046_alter_account_account_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_id',
            field=models.IntegerField(blank=True, default=255025766878975110361680320380373860653, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='bestsubmission',
            name='best_submission_id',
            field=models.IntegerField(blank=True, default=258922610152306027347722825318799690393, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='collection_id',
            field=models.IntegerField(blank=True, default=99617119408089154479842742330779925899, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='collectiongrouppermission',
            name='collection_group_permission_id',
            field=models.IntegerField(blank=True, default=81014014139093807433038406409328592680, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='group_id',
            field=models.IntegerField(blank=True, default=16555706619906256397756149457406660852, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='groupmember',
            name='group_member_id',
            field=models.IntegerField(blank=True, default=327764340289070410599813626795123765411, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='problem_id',
            field=models.IntegerField(blank=True, default=158188918196591434367913126653525869241, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='problemgrouppermission',
            name='problem_group_permission_id',
            field=models.IntegerField(blank=True, default=253268741446266731297890328391178611475, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='submission_id',
            field=models.IntegerField(blank=True, default=24540818810954611023886936486853063157, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='submissiontestcase',
            name='submission_testcase_id',
            field=models.IntegerField(blank=True, default=264396448540576706768031613977560334190, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='testcase',
            name='testcase_id',
            field=models.IntegerField(blank=True, default=85088409562075225550176092152049933143, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='topic_id',
            field=models.IntegerField(blank=True, default=326588415083665992335616674836859249347, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='topicgrouppermission',
            name='topic_group_permission_id',
            field=models.IntegerField(blank=True, default=224958087767984655481777651457017521859, primary_key=True, serialize=False, unique=True),
        ),
    ]