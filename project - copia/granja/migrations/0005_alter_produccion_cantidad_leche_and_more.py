# Generated by Django 5.0.4 on 2024-06-21 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('granja', '0004_alter_produccion_cantidad_leche_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produccion',
            name='cantidad_leche',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='produccion',
            name='cantidad_vendidas',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='produccion',
            name='precio',
            field=models.FloatField(),
        ),
    ]
