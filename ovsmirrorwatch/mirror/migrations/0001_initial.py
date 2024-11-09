# Generated by Django 5.1.3 on 2024-11-09 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OVSMirror',
            fields=[
                ('name', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('health', models.BooleanField(default=None, null=True)),
                ('description', models.TextField()),
            ],
        ),
    ]
