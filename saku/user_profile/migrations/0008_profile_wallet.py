# Generated by Django 4.0.5 on 2023-05-16 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0007_followrelationship_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='wallet',
            field=models.IntegerField(default=0),
        ),
    ]
