# Generated by Django 3.0.5 on 2020-05-19 21:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedly', '0002_auto_20200508_2236'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Followed',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
