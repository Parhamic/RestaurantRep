# Generated by Django 2.0.5 on 2018-07-03 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20180703_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='orderTime',
            field=models.DateTimeField(),
        ),
    ]
