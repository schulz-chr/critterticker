# Generated by Django 4.1 on 2022-08-31 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carousel', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='divefish',
            old_name='idd',
            new_name='id',
        ),
    ]
