
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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
	AIEngine,
	EcoTipView,
	SuggestionKnowledgeEntry,
)

# 1. Register the Custom User model
# We use UserAdmin so the password fields and roles look correct
admin.site.register(User, UserAdmin)

# 2. Register the Expert Profile
admin.site.register(ExpertProfile)

# 3. Register the Item Submissions (the waste items)
admin.site.register(ItemSubmission)

# 4. Register EcoTips and Job Requests for system management
admin.site.register(EcoTip)
admin.site.register(Location)
admin.site.register(Skill)
admin.site.register(RepairExpertSkill)
admin.site.register(Suggestion)
admin.site.register(AIEngine)
admin.site.register(EcoTipView)
admin.site.register(SuggestionKnowledgeEntry)


@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
	list_display = ('id', 'requester', 'expert', 'status', 'is_flagged', 'escalated_for_review', 'created_at')
	list_filter = ('status', 'is_flagged', 'escalated_for_review')
	search_fields = ('requester__username', 'expert__username', 'message', 'admin_note')
