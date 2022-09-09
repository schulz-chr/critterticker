# Generated by Django 4.1 on 2022-09-02 16:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carousel', '0010_alter_divefish_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fish',
            fields=[
                ('id', models.CharField(default='', max_length=5, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('price', models.IntegerField(default=0)),
                ('catches_req', models.IntegerField(default=0, verbose_name='f catches required')),
                ('size', models.CharField(choices=[('XS', 'tiny'), ('S', 'small'), ('M', 'medium'), ('L', 'large'), ('LT', 'long & thin'), ('XL', 'very large'), ('XLF', 'very large (finned)'), ('XXL', 'huge')], default='XS', max_length=20)),
                ('interval_start', models.TimeField(default=datetime.time(0, 0))),
                ('interval_end', models.TimeField(default=datetime.time(23, 59, 59, 999999))),
                ('interval2_start', models.TimeField(default=datetime.time(0, 0))),
                ('interval2_end', models.TimeField(default=datetime.time(23, 59, 59, 999999))),
                ('month', models.ManyToManyField(blank=True, to='carousel.month')),
            ],
            options={
                'verbose_name_plural': 'Fish',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.CharField(default='', max_length=5, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('price', models.IntegerField(default=0)),
                ('catches_req', models.IntegerField(default=0, verbose_name='b catches required')),
                ('interval_start', models.TimeField(default=datetime.time(0, 0))),
                ('interval_end', models.TimeField(default=datetime.time(23, 59, 59, 999999))),
                ('interval2_start', models.TimeField(default=datetime.time(0, 0))),
                ('interval2_end', models.TimeField(default=datetime.time(23, 59, 59, 999999))),
                ('month', models.ManyToManyField(blank=True, to='carousel.month')),
            ],
            options={
                'verbose_name_plural': 'Bugs',
                'ordering': ['name'],
            },
        ),
    ]