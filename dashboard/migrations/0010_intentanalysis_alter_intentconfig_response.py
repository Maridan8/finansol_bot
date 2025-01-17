# Generated by Django 4.2.4 on 2023-09-18 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_remove_productconfig_intent'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntentAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='intentconfig',
            name='response',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
