# Generated by Django 4.0.5 on 2023-05-05 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0014_city_auction_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='city',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='auction.city'),
        ),
    ]
