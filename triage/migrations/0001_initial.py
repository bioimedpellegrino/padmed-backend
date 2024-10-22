# Generated by Django 3.2.7 on 2021-09-19 09:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('generic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('full_address', models.TextField(blank=True, default='', null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hospital_city', to='generic.city')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hospital_country', to='generic.country')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hospital_province', to='generic.province')),
            ],
            options={
                'verbose_name': 'Ospedale',
                'verbose_name_plural': 'Ospedali',
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('fiscal_code', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('first_name', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('middle_name', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('last_name', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('birth_place', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('note', models.TextField(blank=True, default='', null=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'M'), ('F', 'F'), ('O', 'O')], max_length=1, null=True)),
                ('phone', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('email', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('nationality', models.CharField(blank=True, choices=[('italian', 'italian'), ('foreign', 'foreign')], default='italian', max_length=512, null=True)),
                ('has_accept_privacy', models.BooleanField(default=False)),
                ('lang', models.CharField(default='it', max_length=5)),
                ('full_address', models.TextField(blank=True, default='', null=True)),
                ('residence_city_code', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('residence_zip_code', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('domicile_city_code', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('domicile_zip_code', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('domicile_city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='domicile_city', to='generic.city')),
                ('domicile_country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='domicile_country', to='generic.country')),
                ('domicile_province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='domicile_province', to='generic.province')),
                ('hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='triage.hospital')),
                ('residence_city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='residence_city', to='generic.city')),
                ('residence_country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='residence_country', to='generic.country')),
                ('residence_province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='residence_province', to='generic.province')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Paziente',
                'verbose_name_plural': 'Pazienti',
                'ordering': ('last_name',),
            },
        ),
    ]
