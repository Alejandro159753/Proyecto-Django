# Generated by Django 5.1.2 on 2024-11-12 01:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0003_alter_areaexperticia_perfil_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='informacionadicional',
            name='perfil',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='usuario',
        ),
        migrations.DeleteModel(
            name='AreaExperticia',
        ),
        migrations.DeleteModel(
            name='InformacionAdicional',
        ),
        migrations.DeleteModel(
            name='Perfil',
        ),
    ]
