# Generated by Django 2.0.3 on 2018-03-19 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20180319_1105'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='talks',
            new_name='talk',
        ),
    ]
