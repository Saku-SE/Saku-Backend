# Generated by Django 4.0.5 on 2023-04-07 09:04

import bid.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bid', '0005_alter_bid_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='user',
            field=models.ForeignKey(on_delete=models.SET(bid.models.get_default_user_id), to=settings.AUTH_USER_MODEL),
        ),
    ]
