# Generated by Django 4.2.7 on 2023-11-14 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager', '0002_project_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_name', to='taskmanager.project'),
        ),
    ]
