# Generated by Django 3.2.7 on 2021-12-11 09:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('triage', '0011_measurelogger'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurelogger',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
