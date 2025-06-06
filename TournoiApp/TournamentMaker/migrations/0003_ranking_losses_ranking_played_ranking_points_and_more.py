# Generated by Django 5.2 on 2025-05-19 14:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TournamentMaker', '0002_alter_ranking_rank_alter_ranking_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='ranking',
            name='losses',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ranking',
            name='played',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ranking',
            name='points',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ranking',
            name='wins',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ranking',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TournamentMaker.team'),
        ),
    ]
