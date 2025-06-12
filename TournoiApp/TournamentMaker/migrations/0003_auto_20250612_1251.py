from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('TournamentMaker', 'XXXXX_previous_migration'),  # remplace par la dernière migration appliquée
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='tournament',
            field=models.ForeignKey(
                to='TournamentMaker.Tournament',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='matches',
                null=True,
                blank=True,
            ),
        ),
    ]
