# Generated by Django 4.1 on 2022-09-09 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carousel', '0021_alter_image_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Gyroid',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]