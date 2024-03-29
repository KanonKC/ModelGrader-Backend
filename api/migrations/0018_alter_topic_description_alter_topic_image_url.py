# Generated by Django 4.1.2 on 2023-02-24 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_alter_topic_is_active_alter_topic_is_private'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=models.CharField(blank=True, default=None, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='image_url',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='topic/'),
        ),
    ]
