# Generated by Django 4.0.5 on 2023-05-01 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0006_alter_profile_email_alter_profile_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('followed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='user_profile.profile')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to='user_profile.profile')),
            ],
        ),
        migrations.AddConstraint(
            model_name='followrelationship',
            constraint=models.UniqueConstraint(fields=('follower', 'followed'), name='follow_relation_pk'),
        ),
    ]