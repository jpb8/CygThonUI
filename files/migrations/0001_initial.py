# Generated by Django 2.2.2 on 2019-06-06 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DTF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='dtf/')),
                ('uploaded', models.DateTimeField(auto_now=True)),
                ('last_update', models.DateTimeField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Projects')),
            ],
        ),
        migrations.CreateModel(
            name='DDS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='dds/')),
                ('uploaded', models.DateTimeField(auto_now=True)),
                ('last_update', models.DateTimeField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Projects')),
            ],
        ),
    ]
