# Generated by Django 4.2.4 on 2023-09-17 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_productconfig_intent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productconfig',
            name='file',
            field=models.FileField(upload_to=''),
        ),
    ]
