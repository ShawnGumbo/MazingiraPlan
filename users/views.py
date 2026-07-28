from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404

from .models import User, ItemSubmission, EcoTip, JobRequest, ExpertProfile
from .serializers import (
    RegisterSerializer, 
    UserSerializer, 
    MyTokenObtainPairSerializer,
    ItemSubmissionSerializer,
    EcoTipSerializer,
    JobRequestSerializer,
    JobRequestCreateSerializer,
    JobRequestDecisionSerializer,
    JobRequestAdminActionSerializer,
    LocationSerializer,
    SkillSerializer,
    SuggestionKnowledgeEntrySerializer,
    AdminExpertSerializer,
    AdminSubmissionSerializer,
    AdminSubmissionActionSerializer,
)
from .models import Suggestion, AIEngine, EcoTipView, Location, Skill, SuggestionKnowledgeEntry

from google import genai
from google.genai import types
from django.conf import settings
import json


def _is_admin(user):
    return user.role == User.Roles.SYSTEM_ADMIN or user.is_staff


def _normalize_json_response(text):
    cleaned = text.replace('```json', '').replace('```', '').strip()
    return json.loads(cleaned)


def _location_name_for_user(user):
    if user.location:
        return user.location.name
    profile = getattr(user, 'expert_profile', None)
    if profile and profile.location_ref:
        return profile.location_ref.name
    if profile and profile.location:
        return profile.location
    return ''


def _knowledge_entry_for(material_type, location_name):
    query = SuggestionKnowledgeEntry.objects.filter(is_active=True, material_type__iexact=material_type)
    if location_name:
        local = query.filter(location_name__iexact=location_name).first()
        if local:
            return local
    return query.filter(location_name='').first()


def _to_bool(value, default=True):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    lowered = str(value).strip().lower()
    if lowered in ['true', '1', 'yes', 'y', 'on']:
        return True
    if lowered in ['false', '0', 'no', 'n', 'off']:
        return False
    return default


def _extract_response_text(response):
    text = getattr(response, 'text', '') or ''
    if text:
        return text

    try:
        candidates = getattr(response, 'candidates', [])
        if not candidates:
            return ''
        parts = candidates[0].content.parts
        if not parts:
            return ''
        return getattr(parts[0], 'text', '') or ''
    except Exception:
        return ''


def _build_image_part(uploaded_image):
    if not uploaded_image:
        return None

    try:
        uploaded_image.seek(0)
        image_bytes = uploaded_image.read()
        uploaded_image.seek(0)
    except Exception:
        return None

    if not image_bytes:
        return None

    mime_type = getattr(uploaded_image, 'content_type', None) or 'image/jpeg'
    return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)


def _generate_json_with_gemini(client, prompt, image_part=None):
    contents = [prompt]
    if image_part:
        contents.append(image_part)

    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(response_mime_type='application/json'),
    )

    return _normalize_json_response(_extract_response_text(response))

# 1. Login View
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# 2. Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpertListView(generics.ListAPIView):
    queryset = User.objects.filter(role='EXPERT').select_related('expert_profile', 'expert_profile__location_ref').prefetch_related('expert_profile__skill_links__skill')
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# 4. Item Submission View
class ItemSubmissionView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        image = request.FILES.get('image')
        description = request.data.get('description', 'A waste item')
        
        submission = ItemSubmission.objects.create(
            owner=request.user,
            image=image,
            description=description,
            classification_label="Processing..."
        )

        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError('GEMINI_API_KEY is not configured.')

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            identify_prompt = (
                "Identify the likely material and label for this waste item. "
                f"Description: {description}. "
                f"Image provided: {'yes' if image else 'no'}. "
                "Return ONLY JSON with keys: classification, material_type."
            )

            image_part = _build_image_part(image)
            material_data = _generate_json_with_gemini(client, identify_prompt, image_part=image_part)

            suggestions_prompt = (
                "Generate practical reusing and repurposing suggestions for this waste item. "
                f"Description: {description}. "
                f"Material type: {material_data.get('material_type', 'Unknown')}. "
                "Return ONLY JSON with keys: repurpose_idea, diy_project, disposal_method."
            )
            suggestion_data = _generate_json_with_gemini(client, suggestions_prompt)

            ai_engine, _ = AIEngine.objects.get_or_create(name='Gemini', version='1.5-flash')

            ai_data = {
                'classification': material_data.get('classification', 'General Waste'),
                'material_type': material_data.get('material_type', 'Mixed Material'),
                'repurpose_idea': suggestion_data.get('repurpose_idea', 'Reuse as storage or donation material if still safe.'),
                'diy_project': suggestion_data.get('diy_project', 'Clean and transform into a basic organizer project.'),
                'disposal_method': suggestion_data.get('disposal_method', 'Sort and send to an approved local recycling point.'),
            }

            location_name = _location_name_for_user(request.user)
            kb_entry = _knowledge_entry_for(ai_data['material_type'], location_name)
            if kb_entry:
                ai_data['repurpose_idea'] = kb_entry.reuse_idea
                ai_data['diy_project'] = kb_entry.repurpose_idea
                ai_data['disposal_method'] = kb_entry.disposal_guidance

            submission.repurpose_idea = ai_data.get('repurpose_idea')
            submission.diy_project = ai_data.get('diy_project')
            submission.disposal_method = ai_data.get('disposal_method')
            submission.classification_label = ai_data.get('classification', 'General Waste')
            submission.material_type = ai_data.get('material_type', 'Mixed Material')
            submission.ai_engine = ai_engine
            submission.save()

            Suggestion.objects.filter(item=submission).delete()
            Suggestion.objects.create(item=submission, type=Suggestion.Type.REUSE, description=ai_data['repurpose_idea'])
            Suggestion.objects.create(item=submission, type=Suggestion.Type.REPURPOSE, description=ai_data['diy_project'])
            Suggestion.objects.create(item=submission, type=Suggestion.Type.DISPOSAL, description=ai_data['disposal_method'])

            ai_data['suggestions'] = [
                {'type': Suggestion.Type.REUSE, 'description': ai_data['repurpose_idea']},
                {'type': Suggestion.Type.REPURPOSE, 'description': ai_data['diy_project']},
                {'type': Suggestion.Type.DISPOSAL, 'description': ai_data['disposal_method']},
            ]

            return Response(ai_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            submission.classification_label = 'General Waste'
            submission.material_type = 'Mixed Material'
            submission.repurpose_idea = 'No AI suggestion available yet. Try basic reuse or donation.'
            submission.diy_project = 'No DIY guide generated. Try simple upcycling ideas.'
            submission.disposal_method = 'Follow local recycling and waste sorting guidelines.'
            submission.save()

            Suggestion.objects.filter(item=submission).delete()
            Suggestion.objects.create(item=submission, type=Suggestion.Type.REUSE, description=submission.repurpose_idea)
            Suggestion.objects.create(item=submission, type=Suggestion.Type.REPURPOSE, description=submission.diy_project)
            Suggestion.objects.create(item=submission, type=Suggestion.Type.DISPOSAL, description=submission.disposal_method)

            return Response({
                "error": str(e),
                "classification": submission.classification_label,
                "material_type": submission.material_type,
                "repurpose_idea": submission.repurpose_idea,
                "diy_project": submission.diy_project,
                "disposal_method": submission.disposal_method,
                "suggestions": [
                    {'type': Suggestion.Type.REUSE, 'description': submission.repurpose_idea},
                    {'type': Suggestion.Type.REPURPOSE, 'description': submission.diy_project},
                    {'type': Suggestion.Type.DISPOSAL, 'description': submission.disposal_method},
                ]
            }, status=200)


class SubmissionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSubmissionSerializer

    def get_queryset(self):
        return ItemSubmission.objects.filter(owner=self.request.user).order_by('-created_at')


class EcoTipListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tips = EcoTip.objects.order_by('-updated_at')
        if request.user.role == User.Roles.ENVIRONMENTAL_USER:
            existing_tip_ids = set(
                EcoTipView.objects.filter(community_member=request.user).values_list('tip_id', flat=True)
            )
            view_rows = [
                EcoTipView(community_member=request.user, tip=tip)
                for tip in tips
                if tip.id not in existing_tip_ids
            ]
            if view_rows:
                EcoTipView.objects.bulk_create(view_rows)

        return Response(EcoTipSerializer(tips, many=True).data)

    def post(self, request):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can create eco tips.')

        serializer = EcoTipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EcoTipDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, tip_id):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can edit eco tips.')

        tip = get_object_or_404(EcoTip, pk=tip_id)
        serializer = EcoTipSerializer(tip, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, tip_id):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can delete eco tips.')

        tip = get_object_or_404(EcoTip, pk=tip_id)
        tip.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JobRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _is_admin(request.user):
            queryset = JobRequest.objects.select_related('requester', 'expert', 'item_submission').order_by('-created_at')
        elif request.user.role == User.Roles.FIND_EXPERT:
            queryset = JobRequest.objects.select_related('requester', 'expert', 'item_submission').filter(expert=request.user).order_by('-created_at')
        else:
            queryset = JobRequest.objects.select_related('requester', 'expert', 'item_submission').filter(requester=request.user).order_by('-created_at')

        return Response(JobRequestSerializer(queryset, many=True).data)

    def post(self, request):
        if request.user.role != User.Roles.ENVIRONMENTAL_USER:
            raise PermissionDenied('Only community members can create job requests.')

        serializer = JobRequestCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        job_request = serializer.save(requester=request.user)
        output = JobRequestSerializer(job_request)
        return Response(output.data, status=status.HTTP_201_CREATED)


class JobRequestRespondView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        job_request = get_object_or_404(JobRequest, pk=request_id)

        can_respond = _is_admin(request.user) or (
            request.user.role == User.Roles.FIND_EXPERT and job_request.expert_id == request.user.id
        )
        if not can_respond:
            raise PermissionDenied('You are not allowed to respond to this request.')

        if job_request.status != JobRequest.Status.PENDING:
            return Response({'detail': 'This request has already been resolved.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = JobRequestDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']

        next_status = JobRequest.Status.ACCEPTED if action == 'ACCEPT' else JobRequest.Status.REJECTED
        job_request.mark_status(next_status)
        if _is_admin(request.user):
            job_request.append_intervention(request.user.username, action)

        return Response(JobRequestSerializer(job_request).data)


class JobRequestAdminActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can perform this action.')

        job_request = get_object_or_404(JobRequest, pk=request_id)
        serializer = JobRequestAdminActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']
        note = serializer.validated_data.get('note', '')

        if action in ['ACCEPT', 'REJECT']:
            if job_request.status != JobRequest.Status.PENDING:
                return Response({'detail': 'This request has already been resolved.'}, status=status.HTTP_400_BAD_REQUEST)
            next_status = JobRequest.Status.ACCEPTED if action == 'ACCEPT' else JobRequest.Status.REJECTED
            job_request.mark_status(next_status)
        elif action == 'FLAG':
            job_request.is_flagged = True
            job_request.save(update_fields=['is_flagged', 'updated_at'])
        elif action == 'UNFLAG':
            job_request.is_flagged = False
            job_request.save(update_fields=['is_flagged', 'updated_at'])
        elif action == 'ESCALATE':
            job_request.escalated_for_review = True
            job_request.save(update_fields=['escalated_for_review', 'updated_at'])
        elif action == 'NOTE':
            if note:
                job_request.admin_note = note
                job_request.save(update_fields=['admin_note', 'updated_at'])

        job_request.append_intervention(request.user.username, action, note)
        return Response(JobRequestSerializer(job_request).data)


class LocationListView(generics.ListAPIView):
    queryset = Location.objects.order_by('name')
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]


class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.order_by('name')
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]


class AdminDashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can view dashboard summary.')

        payload = {
            'users_count': User.objects.count(),
            'community_members_count': User.objects.filter(role=User.Roles.ENVIRONMENTAL_USER).count(),
            'experts_count': User.objects.filter(role=User.Roles.FIND_EXPERT).count(),
            'verified_experts_count': User.objects.filter(role=User.Roles.FIND_EXPERT, expert_profile__is_verified=True).count(),
            'submissions_count': ItemSubmission.objects.count(),
            'suggestions_count': Suggestion.objects.count(),
            'job_requests_count': JobRequest.objects.count(),
            'knowledge_entries_count': SuggestionKnowledgeEntry.objects.count(),
        }
        return Response(payload)


class AdminSubmissionListView(generics.ListAPIView):
    serializer_class = AdminSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not _is_admin(self.request.user):
            raise PermissionDenied('Only administrators can view all submissions.')
        return ItemSubmission.objects.select_related('owner').order_by('-created_at')


class AdminSubmissionActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, submission_id):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can moderate submissions.')

        submission = get_object_or_404(ItemSubmission, pk=submission_id)
        serializer = AdminSubmissionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission.status = serializer.validated_data['status']
        submission.save(update_fields=['status'])
        return Response(AdminSubmissionSerializer(submission).data)


class AdminExpertListView(generics.ListAPIView):
    serializer_class = AdminExpertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not _is_admin(self.request.user):
            raise PermissionDenied('Only administrators can view experts.')
        return User.objects.filter(role=User.Roles.FIND_EXPERT).select_related('expert_profile')


class AdminExpertVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can approve experts.')

        expert_user = get_object_or_404(User, pk=user_id, role=User.Roles.FIND_EXPERT)
        profile = get_object_or_404(ExpertProfile, user=expert_user)
        profile.is_verified = _to_bool(request.data.get('is_verified', True), default=True)
        profile.save(update_fields=['is_verified'])
        return Response(AdminExpertSerializer(expert_user).data)


class SuggestionKnowledgeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can view suggestion knowledge base.')
        entries = SuggestionKnowledgeEntry.objects.all()
        return Response(SuggestionKnowledgeEntrySerializer(entries, many=True).data)

    def post(self, request):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can create suggestion knowledge entries.')
        serializer = SuggestionKnowledgeEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SuggestionKnowledgeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, entry_id):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can update suggestion knowledge entries.')
        entry = get_object_or_404(SuggestionKnowledgeEntry, pk=entry_id)
        serializer = SuggestionKnowledgeEntrySerializer(entry, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, entry_id):
        if not _is_admin(request.user):
            raise PermissionDenied('Only administrators can delete suggestion knowledge entries.')
        entry = get_object_or_404(SuggestionKnowledgeEntry, pk=entry_id)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)