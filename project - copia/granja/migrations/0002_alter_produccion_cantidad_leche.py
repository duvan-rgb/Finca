# Generated by Django 5.0.4 on 2024-06-21 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('granja', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produccion',
            name='cantidad_leche',
            field=models.FloatField(blank=True),
        ),
    ]
