# Generated by Django 3.2.7 on 2021-12-23 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('triage', '0019_remove_patient_user'),
        ('app', '0010_appuser_img'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appuser',
            old_name='hospital_logged',
            new_name='_dashboard_hospital',
        ),
        migrations.AddField(
            model_name='appuser',
            name='patient_logged',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='triage.patient', verbose_name='Paziente'),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='totem_logged',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='triage.totem', verbose_name='Totem'),
        ),
    ]