# Generated by Django 5.1.2 on 2024-11-07 15:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ideas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ideas',
            name='id_foco_innovacion',
        ),
        migrations.RemoveField(
            model_name='ideas',
            name='id_tipo_innovacion',
        ),
        migrations.DeleteModel(
            name='InnovationFocus',
        ),
        migrations.DeleteModel(
            name='Ideas',
        ),
        migrations.DeleteModel(
            name='InnovationType',
        ),
    ]
