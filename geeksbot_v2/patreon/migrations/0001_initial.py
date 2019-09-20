# Generated by Django 2.2.4 on 2019-09-17 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('guilds', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatreonCreator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.CharField(max_length=50)),
                ('link', models.CharField(max_length=100)),
                ('guild', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guilds.Guild')),
            ],
        ),
        migrations.CreateModel(
            name='PatreonTier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('amount', models.IntegerField(null=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patreon.PatreonCreator')),
                ('guild', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guilds.Guild')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guilds.Role')),
            ],
        ),
    ]
