# Generated by Django 3.2.7 on 2022-02-19 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dfx', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deepaffexpoint',
            name='signal_description',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
