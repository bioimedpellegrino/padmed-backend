# Generated by Django 3.2.7 on 2021-12-07 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='_dashboard_options',
            field=models.TextField(default='{}', verbose_name='Opzioni Dashboard'),
        ),
        migrations.AddField(
            model_name='appuser',
            name='theme',
            field=models.CharField(choices=[('light', 'Chiaro'), ('dark', 'Scuro')], default='light', max_length=512, verbose_name='Tema'),
        ),
    ]
