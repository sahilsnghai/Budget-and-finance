# Generated by Django 4.2.7 on 2023-12-12 11:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TmUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('tm_user_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('created_on', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('modified_by', models.IntegerField(blank=True, null=True)),
                ('modified_on', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'tm_user',
            },
        ),
        migrations.CreateModel(
            name='TmPriority',
            fields=[
                ('tm_priority_id', models.AutoField(primary_key=True, serialize=False)),
                ('priority_name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_on', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('modified_on', models.DateField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'tm_priority',
            },
        ),
        migrations.CreateModel(
            name='TmProject',
            fields=[
                ('tm_project_id', models.AutoField(primary_key=True, serialize=False)),
                ('project_name', models.CharField(max_length=255)),
                ('project_description', models.TextField()),
                ('start_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('created_on', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('modified_on', models.DateField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tm_project',
            },
        ),
        migrations.CreateModel(
            name='TmSourceInfo',
            fields=[
                ('tm_source_info_id', models.AutoField(primary_key=True, serialize=False)),
                ('source_info_name', models.CharField(max_length=255)),
                ('created_on', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('modified_on', models.DateField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'tm_source_info',
            },
        ),
        migrations.CreateModel(
            name='TmStatus',
            fields=[
                ('tm_status_id', models.AutoField(primary_key=True, serialize=False)),
                ('status_name', models.CharField(blank=True, max_length=255, null=True)),
                ('colour', models.CharField(default='green', max_length=255)),
                ('created_on', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('modified_on', models.DateField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'tm_status',
            },
        ),
        migrations.CreateModel(
            name='TmTaskType',
            fields=[
                ('tm_task_type_id', models.AutoField(primary_key=True, serialize=False)),
                ('task_type_name', models.CharField(max_length=250)),
                ('task_type_description', models.TextField()),
                ('created_on', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('modified_on', models.DateField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'tm_task_type',
            },
        ),
        migrations.CreateModel(
            name='TmTaskInfo',
            fields=[
                ('tm_task_info_id', models.AutoField(primary_key=True, serialize=False)),
                ('task_title', models.CharField(max_length=255)),
                ('task_description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(default=django.utils.timezone.now)),
                ('close_date', models.DateField(blank=True, default=django.utils.timezone.now)),
                ('label', models.CharField(blank=True, max_length=255, null=True)),
                ('created_on', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('modified_on', models.DateField(blank=True, default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='reporter', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='assignee', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tm_task_info',
            },
        ),
        migrations.CreateModel(
            name='TmTask',
            fields=[
                ('tm_task_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_on', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('modified_on', models.DateField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('tm_priority', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taskmanager.tmpriority')),
                ('tm_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taskmanager.tmproject')),
                ('tm_source_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='taskmanager.tmsourceinfo')),
                ('tm_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taskmanager.tmstatus')),
                ('tm_task_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='taskmanager.tmtaskinfo')),
                ('tm_task_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taskmanager.tmtasktype')),
                ('tm_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tm_task',
            },
        ),
    ]
