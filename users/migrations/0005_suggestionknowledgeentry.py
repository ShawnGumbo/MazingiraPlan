from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_erd_normalization_entities'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuggestionKnowledgeEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_type', models.CharField(max_length=100)),
                ('location_name', models.CharField(blank=True, max_length=120)),
                ('reuse_idea', models.TextField()),
                ('repurpose_idea', models.TextField()),
                ('disposal_guidance', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['material_type', 'location_name'],
            },
        ),
    ]
