from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import (
    User,
    ExpertProfile,
    ItemSubmission,
    EcoTip,
    JobRequest,
    Location,
    Skill,
    RepairExpertSkill,
    Suggestion,
    SuggestionKnowledgeEntry,
)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ['id', 'type', 'description']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Keep role claim aligned with effective privileges for frontend routing.
        effective_role = user.role
        if user.is_staff or user.is_superuser:
            effective_role = User.Roles.SYSTEM_ADMIN

        token['username'] = user.username
        token['role'] = effective_role
        return token

class UserSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'location', 'skills', 'is_verified', 'rating']

    def get_location(self, obj):
        profile = getattr(obj, 'expert_profile', None)
        if profile and profile.location_ref:
            return profile.location_ref.name
        if profile and profile.location:
            return profile.location
        if obj.location:
            return obj.location.name
        return ''

    def get_skills(self, obj):
        profile = getattr(obj, 'expert_profile', None)
        if not profile:
            return []

        linked = list(
            profile.skill_links.select_related('skill').values_list('skill__name', flat=True)
        )
        if linked:
            return linked

        if profile.skills:
            return [part.strip() for part in profile.skills.split(',') if part.strip()]

        return []

    def get_is_verified(self, obj):
        profile = getattr(obj, 'expert_profile', None)
        return bool(profile.is_verified) if profile else False

    def get_rating(self, obj):
        profile = getattr(obj, 'expert_profile', None)
        return float(profile.rating) if profile else 0.0

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    location_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'location_id']

    def validate_role(self, value):
        if value == User.Roles.SYSTEM_ADMIN:
            raise serializers.ValidationError('Administrator accounts cannot be self-registered.')
        return value

    def create(self, validated_data):
        location_id = validated_data.pop('location_id', None)
        location = None
        if location_id:
            location = Location.objects.filter(pk=location_id).first()

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'USER'),
            location=location,
        )
        if user.role == User.Roles.FIND_EXPERT:
            profile, _ = ExpertProfile.objects.get_or_create(user=user)
            if location:
                profile.location_ref = location
                profile.location = location.name
                profile.save(update_fields=['location_ref', 'location'])
        return user


class ItemSubmissionSerializer(serializers.ModelSerializer):
    suggestions = SuggestionSerializer(many=True, read_only=True)

    class Meta:
        model = ItemSubmission
        fields = [
            'id',
            'owner',
            'description',
            'classification_label',
            'material_type',
            'repurpose_idea',
            'diy_project',
            'disposal_method',
            'suggestions',
            'status',
            'created_at',
        ]
        read_only_fields = ['owner', 'status', 'created_at']


class EcoTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoTip
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class JobRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.username', read_only=True)
    expert_name = serializers.CharField(source='expert.username', read_only=True)

    class Meta:
        model = JobRequest
        fields = [
            'id',
            'requester',
            'requester_name',
            'expert',
            'expert_name',
            'item_submission',
            'message',
            'status',
            'is_flagged',
            'escalated_for_review',
            'admin_note',
            'intervention_log',
            'responded_at',
            'created_at',
        ]
        read_only_fields = ['requester', 'status', 'responded_at', 'created_at']


class JobRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequest
        fields = ['expert', 'item_submission', 'message']

    def validate_expert(self, value):
        if value.role != User.Roles.FIND_EXPERT:
            raise serializers.ValidationError('Selected user is not a repair expert.')
        return value

    def validate_item_submission(self, value):
        request = self.context.get('request')
        if value and request and value.owner_id != request.user.id:
            raise serializers.ValidationError('You can only attach your own submitted item.')
        return value


class JobRequestDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['ACCEPT', 'REJECT'])


class JobRequestAdminActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['ACCEPT', 'REJECT', 'FLAG', 'UNFLAG', 'ESCALATE', 'NOTE'])
    note = serializers.CharField(required=False, allow_blank=True)


class SuggestionKnowledgeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestionKnowledgeEntry
        fields = [
            'id',
            'material_type',
            'location_name',
            'reuse_idea',
            'repurpose_idea',
            'disposal_guidance',
            'is_active',
            'updated_at',
        ]


class AdminExpertSerializer(serializers.ModelSerializer):
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_verified']

    def get_is_verified(self, obj):
        profile = getattr(obj, 'expert_profile', None)
        return bool(profile.is_verified) if profile else False


class AdminSubmissionSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = ItemSubmission
        fields = [
            'id',
            'owner_name',
            'description',
            'material_type',
            'classification_label',
            'status',
            'created_at',
        ]


class AdminSubmissionActionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            ItemSubmission.Status.PENDING,
            ItemSubmission.Status.ACCEPTED,
            ItemSubmission.Status.COMPLETED,
            ItemSubmission.Status.REJECTED,
        ]
    )
