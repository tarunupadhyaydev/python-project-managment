# Generated by Django 5.0.6 on 2024-05-30 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('time_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timetracker',
            options={'verbose_name': 'Timesheet', 'verbose_name_plural': 'Timesheet'},
        ),
    ]
