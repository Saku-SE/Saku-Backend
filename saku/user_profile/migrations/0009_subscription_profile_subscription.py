# Generated by Django 4.0.5 on 2023-05-16 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0008_profile_wallet'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('duration', models.IntegerField()),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='subscription',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_profile.subscription'),
        ),
    ]
