# Generated by Django 3.2.7 on 2022-02-27 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('triage', '0019_remove_patient_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='triageaccess',
            name='_status',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
