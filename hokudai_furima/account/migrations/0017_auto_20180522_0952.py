# Generated by Django 2.0.3 on 2018-05-22 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_auto_20180520_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='icon',
            field=models.ImageField(blank=True, upload_to='media/public', verbose_name=''),
        ),
    ]
