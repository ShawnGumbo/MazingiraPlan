# Functional Requirements Traceability

This document maps each functional requirement to implemented backend/frontend modules and validation evidence.

## FR-01 Authentication and Role Access

- Requirement: Community members, experts, and administrators can register/login with role-based access.
- Backend:
  - `POST /api/register/` in `users/views.py` (`RegisterView`)
  - `POST /api/token/` in `users/views.py` (`MyTokenObtainPairView`)
  - Role model in `users/models.py` (`User.Roles`)
- Frontend:
  - `frontend/src/pages/AuthPage.jsx`
  - `frontend/src/App.jsx` route and navigation guards
- Tests:
  - `users/tests.py` registration/login coverage (`test_register_login_and_expert_list`).

## FR-02 Item Upload and AI Material Classification

- Requirement: User uploads image/description and receives AI classification.
- Backend:
  - `POST /api/submit-item/` in `users/views.py` (`ItemSubmissionView`)
  - `users/models.py` (`ItemSubmission` classification fields)
  - AI engine metadata via `users/models.py` (`AIEngine`)
- Frontend:
  - `frontend/src/pages/ItemUploadPage.jsx`
- Tests:
  - `users/tests.py` auth protection (`test_submit_item_requires_auth`).

## FR-03 Reuse/Repurpose/Disposal Suggestions

- Requirement: System recommends reuse, repurpose, and disposal guidance.
- Backend:
  - Suggestion persistence in `users/views.py` (`ItemSubmissionView` creates `Suggestion` rows)
  - `users/models.py` (`Suggestion`)
- Frontend:
  - `frontend/src/pages/SuggestionsPage.jsx`

## FR-04 Curated Knowledge Base for Recommendations

- Requirement: Recommendations follow a curated knowledge base, local-context aware.
- Backend:
  - `users/models.py` (`SuggestionKnowledgeEntry`)
  - `GET/POST /api/admin/knowledge-base/` in `users/views.py` (`SuggestionKnowledgeListCreateView`)
  - `PUT/DELETE /api/admin/knowledge-base/<id>/` in `users/views.py` (`SuggestionKnowledgeDetailView`)
  - `ItemSubmissionView` applies matching knowledge entry by material + location fallback
- Admin:
  - Django admin registration in `users/admin.py`.

## FR-05 Expert Directory and Map Navigation

- Requirement: Users browse experts with location-aware navigation.
- Backend:
  - `GET /api/experts/` in `users/views.py` (`ExpertListView`, public access)
  - Location/skill reference data in `users/models.py` and `users/views.py`
- Frontend:
  - `frontend/src/pages/ExpertDirectory.jsx`
  - Leaflet + OpenStreetMap integration in `frontend/src/main.jsx` and page map component.

## FR-05B My Repurposing Journey

- Requirement: Logged-in users can view their past item submissions and AI suggestions timeline.
- Backend:
  - `GET /api/my-items/` in `users/urls.py` mapped to `SubmissionListView`
  - Backward-compatible alias: `GET /api/submissions/`
- Frontend:
  - `frontend/src/pages/MyItemsPage.jsx`
  - `frontend/src/App.jsx` route `/my-items`

## FR-06 Expert Connection Requests and Responses

- Requirement: Community members request expert assistance; experts/admin respond.
- Backend:
  - `GET/POST /api/job-requests/` (`JobRequestListCreateView`)
  - `POST /api/job-requests/<id>/respond/` (`JobRequestRespondView`)
  - Admin action endpoint `POST /api/job-requests/<id>/admin-action/` (`JobRequestAdminActionView`)
  - `users/models.py` (`JobRequest` workflow and moderation fields)
- Frontend:
  - `frontend/src/pages/ConnectionRequestsPage.jsx`
- Tests:
  - `users/tests.py` lifecycle coverage (`test_job_request_flow`).

## FR-07 Eco-Tips Knowledge Sharing and Community Interaction

- Requirement: Experts/admin publish eco-tips; users can consume tips and community exposure is tracked.
- Backend:
  - `GET/POST /api/eco-tips/` (`EcoTipListCreateView`)
  - `GET/PUT/DELETE /api/eco-tips/<id>/` (`EcoTipDetailView`)
  - View tracking in `users/models.py` (`EcoTipView`) updated in detail endpoint
- Frontend:
  - `frontend/src/pages/EcoTipsPage.jsx`
- Tests:
  - `users/tests.py` admin-only create guard (`test_eco_tip_create_admin_only`).

## FR-08 Administrator Monitoring Dashboard

- Requirement: Administrator can monitor system activity and key counts.
- Backend:
  - `GET /api/admin/dashboard-summary/` in `users/views.py` (`AdminDashboardSummaryView`)
  - `GET /api/admin/submissions/` in `users/views.py` (`AdminSubmissionListView`)
- Frontend:
  - `frontend/src/pages/AdminPanel.jsx` consumes summary endpoint and renders dashboard widgets.

## FR-09 Administrator Expert Verification Workflow

- Requirement: Administrator verifies experts before trust indicators are shown.
- Backend:
  - `GET /api/admin/experts/` (`AdminExpertListView`)
  - `POST /api/admin/experts/<user_id>/verify/` (`AdminExpertVerifyView`)
  - `users/models.py` (`ExpertProfile.is_verified`)
- Frontend:
  - `frontend/src/pages/AdminPanel.jsx` includes Approve/Unapprove controls.

## FR-10 Data Governance and Access Control

- Requirement: Restricted operations are role-protected and auditable.
- Backend Controls:
  - `IsAuthenticated` + explicit role checks (`_is_admin`, role checks in create/update paths)
  - Admin-specific moderation and approval APIs under `/api/admin/...`
  - Job request intervention notes and escalation fields in `users/models.py`.

## Validation Snapshot

- Automated tests currently cover key smoke scenarios in `users/tests.py`.
- Recommended next hardening:
  - Add tests for `/api/admin/dashboard-summary/`
  - Add tests for `/api/admin/experts/<id>/verify/`
  - Add tests for knowledge-base CRUD and suggestion override behavior.