from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_itemsubmission_material_type_ecotip_jobrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='expertprofile',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name='jobrequest',
            name='admin_note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='jobrequest',
            name='escalated_for_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobrequest',
            name='intervention_log',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='jobrequest',
            name='is_flagged',
            field=models.BooleanField(default=False),
        ),
    ]
