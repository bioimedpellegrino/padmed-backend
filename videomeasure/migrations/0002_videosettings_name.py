# Generated by Django 3.2.7 on 2022-10-15 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videomeasure', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='videosettings',
            name='name',
            field=models.CharField(blank=True, default='', max_length=2048, null=True, verbose_name='Nome'),
        ),
    ]
