from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_expertprofile_rating_jobrequest_admin_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIEngine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Gemini', max_length=100)),
                ('version', models.CharField(default='1.5-flash', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='community_members', to='users.location'),
        ),
        migrations.AddField(
            model_name='itemsubmission',
            name='ai_engine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analyzed_items', to='users.aiengine'),
        ),
        migrations.AddField(
            model_name='expertprofile',
            name='location_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repair_experts', to='users.location'),
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('REUSE', 'Reusing Suggestion'), ('REPURPOSE', 'Repurposing Suggestion'), ('DISPOSAL', 'Disposal Suggestion')], max_length=20)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to='users.itemsubmission')),
            ],
        ),
        migrations.CreateModel(
            name='RepairExpertSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skill_links', to='users.expertprofile')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expert_links', to='users.skill')),
            ],
            options={
                'unique_together': {('expert', 'skill')},
            },
        ),
        migrations.CreateModel(
            name='EcoTipView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('community_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eco_tip_views', to=settings.AUTH_USER_MODEL)),
                ('tip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='users.ecotip')),
            ],
            options={
                'unique_together': {('community_member', 'tip')},
            },
        ),
    ]
