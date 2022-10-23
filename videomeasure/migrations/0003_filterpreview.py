# Generated by Django 3.2.7 on 2022-10-23 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('videomeasure', '0002_videosettings_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilterPreview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_image', models.ImageField(upload_to='original_image')),
                ('filtered_image', models.ImageField(upload_to='filtered_image')),
                ('video_setting', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='videomeasure.videosettings')),
            ],
            options={
                'verbose_name': 'Anteprima filtri',
                'verbose_name_plural': 'Anteprime filtri',
            },
        ),
    ]
