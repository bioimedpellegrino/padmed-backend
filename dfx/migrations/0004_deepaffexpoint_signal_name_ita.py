# Generated by Django 3.2.7 on 2022-04-11 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dfx', '0003_deepaffexpoint_is_measure'),
    ]

    operations = [
        migrations.AddField(
            model_name='deepaffexpoint',
            name='signal_name_ita',
            field=models.CharField(blank=True, default='', max_length=1024, null=True),
        ),
    ]
