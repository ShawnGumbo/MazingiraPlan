# Panolive Folder Structure

## Root

- manage.py: Django management entrypoint
- requirements.txt: Backend Python dependencies
- panolive_backend/: Django project configuration
- users/: Core domain app (auth, submissions, experts, eco tips, connection requests)
- frontend/: React client application
- docs/: Documentation and architecture artifacts

## Documentation

- docs/architecture/class_diagram.mmd
- docs/architecture/sequence_diagrams.md

## Frontend

- frontend/src/main.jsx: React entrypoint
- frontend/src/App.jsx: Route shell and role-aware navigation
- frontend/src/App.css: Global UI styling
- frontend/src/index.css: Base styles and CSS variables
- frontend/src/pages/: Route-level pages and actor flows
- frontend/src/services/api.js: Axios API bridge
- frontend/src/utils/auth.js: Session and token helpers

## Frontend Page Flow

- LandingPage.jsx: Public entry
- AuthPage.jsx: Community and expert auth
- AdminLoginPage.jsx: Admin auth
- Dashboard.jsx: Role-specific navigation hub
- ItemUpload.jsx: Community item submission
- SuggestionsPage.jsx: AI output and suggestion view
- ExpertDirectory.jsx: Expert discovery and request initiation
- EcoTipsPage.jsx: Eco tips consumption and admin moderation
- ConnectionRequestsPage.jsx: Expert/admin request handling
- AdminPanel.jsx: Admin overview and control links

## Backend Use-Case Mapping

- users/models.py: User, ExpertProfile, ItemSubmission, EcoTip, JobRequest
- users/views.py: APIs for login/register, upload, experts, eco tips, connection requests
- users/serializers.py: API payload contracts and validation
- users/urls.py: API endpoint routing
- users/tests.py: Behavior tests for key actor flows
