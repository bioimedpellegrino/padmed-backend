# Generated by Django 3.2.7 on 2021-10-10 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('triage', '0003_patientvideo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientvideo',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
