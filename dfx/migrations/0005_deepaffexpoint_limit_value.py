# Generated by Django 3.2.7 on 2022-11-27 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dfx', '0004_deepaffexpoint_signal_name_ita'),
    ]

    operations = [
        migrations.AddField(
            model_name='deepaffexpoint',
            name='limit_value',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
