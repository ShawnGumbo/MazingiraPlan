from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User, ExpertProfile, ItemSubmission, SuggestionKnowledgeEntry


class UsersApiSmokeTests(APITestCase):
	def _login(self, username, password='StrongPass123!'):
		response = self.client.post(
			reverse('token_obtain_pair'),
			{'username': username, 'password': password},
			format='json'
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		return response.data['access']

	def test_register_login_and_experts_listing(self):
		register_payload = {
			'username': 'smoke_user',
			'email': 'smoke@example.com',
			'password': 'StrongPass123!',
			'role': 'USER',
		}
		register_response = self.client.post(reverse('register'), register_payload, format='json')
		self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

		login_payload = {
			'username': 'smoke_user',
			'password': 'StrongPass123!',
		}
		login_response = self.client.post(reverse('token_obtain_pair'), login_payload, format='json')
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)
		self.assertIn('access', login_response.data)
		self.assertIn('refresh', login_response.data)
		access = login_response.data['access']

		User.objects.create_user(
			username='expert_one',
			email='expert@example.com',
			password='StrongPass123!',
			role='EXPERT',
		)
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
		experts_response = self.client.get(reverse('expert-list'))
		self.assertEqual(experts_response.status_code, status.HTTP_200_OK)
		self.assertTrue(any(item['username'] == 'expert_one' for item in experts_response.data))

	def test_experts_listing_is_public(self):
		User.objects.create_user(
			username='public_expert',
			email='public_expert@example.com',
			password='StrongPass123!',
			role='EXPERT',
		)
		response = self.client.get(reverse('expert-list'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(any(item['username'] == 'public_expert' for item in response.data))

	def test_my_items_returns_only_current_user_submissions(self):
		owner = User.objects.create_user(
			username='owner_user',
			email='owner_user@example.com',
			password='StrongPass123!',
			role='USER',
		)
		other = User.objects.create_user(
			username='other_user',
			email='other_user@example.com',
			password='StrongPass123!',
			role='USER',
		)

		ItemSubmission.objects.create(owner=owner, description='Owner item')
		ItemSubmission.objects.create(owner=other, description='Other item')

		token = self._login('owner_user')
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

		response = self.client.get(reverse('my-items'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['description'], 'Owner item')

	def test_submit_item_requires_authentication(self):
		response = self.client.post(reverse('submit-item'), data={})
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_job_request_lifecycle_for_user_and_expert(self):
		member = User.objects.create_user(
			username='member_user',
			email='member@example.com',
			password='StrongPass123!',
			role='USER',
		)
		expert = User.objects.create_user(
			username='expert_user',
			email='expert2@example.com',
			password='StrongPass123!',
			role='EXPERT',
		)

		member_login = self.client.post(
			reverse('token_obtain_pair'),
			{'username': 'member_user', 'password': 'StrongPass123!'},
			format='json'
		)
		member_token = member_login.data['access']
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {member_token}')

		create_response = self.client.post(
			reverse('job-request-list-create'),
			{'expert': expert.id, 'message': 'Need repair support'},
			format='json'
		)
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
		request_id = create_response.data['id']

		expert_login = self.client.post(
			reverse('token_obtain_pair'),
			{'username': 'expert_user', 'password': 'StrongPass123!'},
			format='json'
		)
		expert_token = expert_login.data['access']
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {expert_token}')

		list_response = self.client.get(reverse('job-request-list-create'))
		self.assertEqual(list_response.status_code, status.HTTP_200_OK)
		self.assertTrue(any(item['id'] == request_id for item in list_response.data))

		respond_response = self.client.post(
			reverse('job-request-respond', kwargs={'request_id': request_id}),
			{'action': 'ACCEPT'},
			format='json'
		)
		self.assertEqual(respond_response.status_code, status.HTTP_200_OK)
		self.assertEqual(respond_response.data['status'], 'ACCEPTED')

	def test_only_admin_can_create_eco_tip(self):
		member = User.objects.create_user(
			username='eco_member',
			email='eco_member@example.com',
			password='StrongPass123!',
			role='USER',
		)

		member_login = self.client.post(
			reverse('token_obtain_pair'),
			{'username': 'eco_member', 'password': 'StrongPass123!'},
			format='json'
		)
		member_token = member_login.data['access']
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {member_token}')

		forbidden_response = self.client.post(
			reverse('eco-tip-list-create'),
			{'content': 'Sort glass by color before recycling.'},
			format='json'
		)
		self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

		admin_user = User.objects.create_user(
			username='eco_admin',
			email='eco_admin@example.com',
			password='StrongPass123!',
			role='ADMIN',
			is_staff=True,
		)

		admin_login = self.client.post(
			reverse('token_obtain_pair'),
			{'username': 'eco_admin', 'password': 'StrongPass123!'},
			format='json'
		)
		admin_token = admin_login.data['access']
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')

		created_response = self.client.post(
			reverse('eco-tip-list-create'),
			{'content': 'Sort glass by color before recycling.'},
			format='json'
		)
		self.assertEqual(created_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(created_response.data['content'], 'Sort glass by color before recycling.')

	def test_admin_dashboard_summary_and_expert_verification(self):
		admin = User.objects.create_user(
			username='ops_admin',
			email='ops_admin@example.com',
			password='StrongPass123!',
			role='ADMIN',
			is_staff=True,
		)
		expert = User.objects.create_user(
			username='verify_me',
			email='verify_me@example.com',
			password='StrongPass123!',
			role='EXPERT',
		)
		profile = ExpertProfile.objects.create(user=expert)
		self.assertFalse(profile.is_verified)

		admin_token = self._login('ops_admin')
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')

		summary_response = self.client.get(reverse('admin-dashboard-summary'))
		self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
		self.assertIn('users_count', summary_response.data)
		self.assertIn('suggestions_count', summary_response.data)

		unverify_response = self.client.post(
			reverse('admin-expert-verify', kwargs={'user_id': expert.id}),
			{'is_verified': 'false'},
			format='json'
		)
		self.assertEqual(unverify_response.status_code, status.HTTP_200_OK)
		profile.refresh_from_db()
		self.assertFalse(profile.is_verified)

		verify_response = self.client.post(
			reverse('admin-expert-verify', kwargs={'user_id': expert.id}),
			{'is_verified': True},
			format='json'
		)
		self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
		profile.refresh_from_db()
		self.assertTrue(profile.is_verified)

	def test_admin_submission_moderation_endpoint(self):
		admin = User.objects.create_user(
			username='mod_admin',
			email='mod_admin@example.com',
			password='StrongPass123!',
			role='ADMIN',
			is_staff=True,
		)
		member = User.objects.create_user(
			username='submitter',
			email='submitter@example.com',
			password='StrongPass123!',
			role='USER',
		)
		submission = ItemSubmission.objects.create(owner=member, description='Used plastic bottle')

		admin_token = self._login('mod_admin')
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')

		response = self.client.post(
			reverse('admin-submission-action', kwargs={'submission_id': submission.id}),
			{'status': 'ACCEPTED'},
			format='json'
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		submission.refresh_from_db()
		self.assertEqual(submission.status, 'ACCEPTED')

	def test_knowledge_base_admin_only_create(self):
		member = User.objects.create_user(
			username='kb_member',
			email='kb_member@example.com',
			password='StrongPass123!',
			role='USER',
		)
		member_token = self._login('kb_member')
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {member_token}')

		forbidden_response = self.client.post(
			reverse('admin-knowledge-base-list-create'),
			{
				'material_type': 'Plastic',
				'location_name': '',
				'reuse_idea': 'Use as seedling tray.',
				'repurpose_idea': 'Cut into storage cup.',
				'disposal_guidance': 'Bring to plastics recycling.',
			},
			format='json'
		)
		self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

		admin = User.objects.create_user(
			username='kb_admin',
			email='kb_admin@example.com',
			password='StrongPass123!',
			role='ADMIN',
			is_staff=True,
		)
		admin_token = self._login('kb_admin')
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')

		created_response = self.client.post(
			reverse('admin-knowledge-base-list-create'),
			{
				'material_type': 'Plastic',
				'location_name': '',
				'reuse_idea': 'Use as seedling tray.',
				'repurpose_idea': 'Cut into storage cup.',
				'disposal_guidance': 'Bring to plastics recycling.',
			},
			format='json'
		)
		self.assertEqual(created_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(SuggestionKnowledgeEntry.objects.count(), 1)
