# Generated by Django 5.0.3 on 2024-04-01 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='isGraduate',
            field=models.BooleanField(default=False, verbose_name='Is Graduated'),
        ),
    ]
