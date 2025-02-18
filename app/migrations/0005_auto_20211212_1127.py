# Generated by Django 3.2.7 on 2021-12-12 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('app', '0004_appgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='appgroup',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='appgroup',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='appgroup',
            name='tag',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
    ]
