# Generated by Django 3.1.5 on 2021-08-31 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_auto_20210830_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='text',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
