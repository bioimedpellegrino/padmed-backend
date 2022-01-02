# Generated by Django 3.2.7 on 2021-12-15 22:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('triage', '0014_remove_hospital_app_groups'),
        ('app', '0007_auto_20211212_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='hospital_logged',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='triage.hospital', verbose_name='Ospedalle attualmente loggato'),
        ),
    ]