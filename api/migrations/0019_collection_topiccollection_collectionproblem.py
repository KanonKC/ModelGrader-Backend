# Generated by Django 4.1.2 on 2023-04-22 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_topic_description_alter_topic_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('collection_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, default=None, max_length=1000, null=True)),
                ('is_active', models.BooleanField(blank=True, default=False)),
                ('is_private', models.BooleanField(blank=True, default=True)),
            ],
        ),
        migrations.CreateModel(
            name='TopicCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.ForeignKey(db_column='collection_id', on_delete=django.db.models.deletion.CASCADE, to='api.collection')),
                ('topic', models.ForeignKey(db_column='topic_id', on_delete=django.db.models.deletion.CASCADE, to='api.topic')),
            ],
        ),
        migrations.CreateModel(
            name='CollectionProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.ForeignKey(db_column='collection_id', on_delete=django.db.models.deletion.CASCADE, to='api.collection')),
                ('problem', models.ForeignKey(db_column='problem_id', on_delete=django.db.models.deletion.CASCADE, to='api.problem')),
            ],
        ),
    ]
