# Generated by Django 2.0.4 on 2018-07-04 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='workBegan',
            field=models.TimeField(blank=True, null=True),
        ),
    ]