# Generated by Django 3.2.20 on 2023-08-14 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20230814_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdfname',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
