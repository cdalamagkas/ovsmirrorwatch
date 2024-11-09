# Generated by Django 5.1.3 on 2024-11-09 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OVSManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('port', models.IntegerField(default=6640)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField()),
                ('monitor', models.BooleanField(default=False)),
            ],
        ),
    ]
