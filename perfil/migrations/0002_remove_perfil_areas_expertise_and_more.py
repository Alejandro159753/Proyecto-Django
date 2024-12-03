# Generated by Django 5.1.2 on 2024-10-30 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perfil',
            name='areas_expertise',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='info_adicional',
        ),
        migrations.CreateModel(
            name='AreaExperticia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(max_length=100)),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='perfil.perfil')),
            ],
        ),
        migrations.CreateModel(
            name='InformacionAdicional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.TextField()),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='perfil.perfil')),
            ],
        ),
    ]