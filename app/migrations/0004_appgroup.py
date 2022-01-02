# Generated by Django 3.2.7 on 2021-12-11 14:38

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('app', '0003_alter_appuser_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppGroup',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.group')),
            ],
            options={
                'verbose_name': 'Application Group',
                'verbose_name_plural': 'Application Groups',
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
    ]