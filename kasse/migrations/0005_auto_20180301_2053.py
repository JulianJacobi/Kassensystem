# Generated by Django 2.0.1 on 2018-03-01 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasse', '0004_auto_20180227_1928'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Name')),
                ('start', models.DateTimeField(verbose_name='Start')),
                ('end', models.DateTimeField(verbose_name='Ende')),
            ],
        ),
        migrations.AddField(
            model_name='accountentry',
            name='user',
            field=models.CharField(default='', max_length=200, verbose_name='Benutzer'),
        ),
    ]
