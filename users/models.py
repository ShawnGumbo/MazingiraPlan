
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Location(models.Model):
	name = models.CharField(max_length=120, unique=True)

	def __str__(self):
		return self.name


class AIEngine(models.Model):
	name = models.CharField(max_length=100, default='Gemini')
	version = models.CharField(max_length=100, default='1.5-flash')

	def __str__(self):
		return f"{self.name} {self.version}"

# 1. The User Model (Handles Login & Roles)
class User(AbstractUser):
	class Roles(models.TextChoices):
		ENVIRONMENTAL_USER = 'USER', 'Environmental User'
		FIND_EXPERT = 'EXPERT', 'Repair Expert'
		SYSTEM_ADMIN = 'ADMIN', 'System Administrator'

	role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.ENVIRONMENTAL_USER)
	location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='community_members')

# 2. The Expert Profile (Extra info for repair experts)
class ExpertProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='expert_profile')
	location = models.CharField(max_length=255, blank=True, null=True)
	location_ref = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='repair_experts')
	skills = models.TextField(blank=True, null=True)
	is_verified = models.BooleanField(default=False)
	rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

	def __str__(self):
		return f"{self.user.username}'s Expert Profile"

# 3. Item Submission (The items users want to repurpose)
class ItemSubmission(models.Model):
	class Status(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		ACCEPTED = 'ACCEPTED', 'Accepted'
		COMPLETED = 'COMPLETED', 'Completed'
		REJECTED = 'REJECTED', 'Rejected'

	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
	image = models.ImageField(upload_to='submissions/', blank=True, null=True)
	description = models.TextField()
	classification_label = models.CharField(max_length=100, blank=True)
	material_type = models.CharField(max_length=100, blank=True)
    
	# AI-generated guidance fields
	repurpose_idea = models.TextField(blank=True)
	diy_project = models.TextField(blank=True)
	disposal_method = models.TextField(blank=True)
	ai_engine = models.ForeignKey(AIEngine, on_delete=models.SET_NULL, null=True, blank=True, related_name='analyzed_items')
    
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.classification_label or 'Item'} by {self.owner.username}"


class Suggestion(models.Model):
	class Type(models.TextChoices):
		REUSE = 'REUSE', 'Reusing Suggestion'
		REPURPOSE = 'REPURPOSE', 'Repurposing Suggestion'
		DISPOSAL = 'DISPOSAL', 'Disposal Suggestion'

	item = models.ForeignKey(ItemSubmission, on_delete=models.CASCADE, related_name='suggestions')
	type = models.CharField(max_length=20, choices=Type.choices)
	description = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.type} for item {self.item_id}"


class SuggestionKnowledgeEntry(models.Model):
	material_type = models.CharField(max_length=100)
	location_name = models.CharField(max_length=120, blank=True)
	reuse_idea = models.TextField()
	repurpose_idea = models.TextField()
	disposal_guidance = models.TextField()
	is_active = models.BooleanField(default=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['material_type', 'location_name']

	def __str__(self):
		label = self.material_type
		if self.location_name:
			label = f"{label} ({self.location_name})"
		return label


class Skill(models.Model):
	name = models.CharField(max_length=120, unique=True)

	def __str__(self):
		return self.name


class RepairExpertSkill(models.Model):
	expert = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, related_name='skill_links')
	skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='expert_links')

	class Meta:
		unique_together = ('expert', 'skill')

	def __str__(self):
		return f"{self.expert.user.username} - {self.skill.name}"


class EcoTip(models.Model):
	content = models.TextField()
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='eco_tips_created'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.content[:45]


class EcoTipView(models.Model):
	community_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eco_tip_views')
	tip = models.ForeignKey(EcoTip, on_delete=models.CASCADE, related_name='views')
	viewed_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('community_member', 'tip')

	def __str__(self):
		return f"{self.community_member.username} viewed tip {self.tip_id}"


class JobRequest(models.Model):
	class Status(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		ACCEPTED = 'ACCEPTED', 'Accepted'
		REJECTED = 'REJECTED', 'Rejected'

	requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_requests_sent')
	expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_requests_received')
	item_submission = models.ForeignKey(
		ItemSubmission,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='job_requests'
	)
	message = models.TextField(blank=True)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
	is_flagged = models.BooleanField(default=False)
	escalated_for_review = models.BooleanField(default=False)
	admin_note = models.TextField(blank=True)
	intervention_log = models.TextField(blank=True)
	responded_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def mark_status(self, next_status):
		self.status = next_status
		self.responded_at = timezone.now()
		self.save(update_fields=['status', 'responded_at', 'updated_at'])

	def append_intervention(self, username, action, note=''):
		timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
		entry = f"[{timestamp}] {username}: {action}"
		if note:
			entry = f"{entry} ({note})"

		self.intervention_log = f"{self.intervention_log}\n{entry}".strip()
		self.save(update_fields=['intervention_log', 'updated_at'])

	def __str__(self):
		return f"Request {self.id} from {self.requester.username} to {self.expert.username}"
