# Generated by Django 2.2 on 2019-04-20 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasse', '0005_auto_20180301_2053'),
    ]

    operations = [
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Name')),
                ('pos_x', models.FloatField()),
                ('pos_y', models.FloatField()),
                ('size_x', models.FloatField()),
                ('size_y', models.FloatField()),
                ('bookings', models.TextField()),
            ],
        ),
    ]