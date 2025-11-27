Overview
========

Lightweight Django REST API for creating, updating, browsing, and registering for UMASS events. The service exposes a JSON-first ``/api/`` surface, uses JWT authentication shared with the user-auth service, and ships with sample data for quick demos.

Highlights
----------
- Built with Django 5 + Django REST Framework; ships with SQLite for local development.
- JWT-based auth via ``ExternalJWTAuthentication`` with role-aware permissions (student/staff/admin).
- Core domain: ``Event`` records with capacity, registration roster, schedule, hosting details, and links.
- Filtering, searching, sorting, and capacity-aware queries to support multiple event discovery flows.

Project Structure
-----------------

:: 

   eventsService/
   ├─ manage.py                 # Django entrypoint
   ├─ eventsService/            # Project settings, URLs, auth
   │  ├─ settings.py
   │  ├─ urls.py
   │  └─ authentication.py
   ├─ api/                      # REST API layer
   │  ├─ views.py               # Endpoint implementations
   │  ├─ urls.py                # /api/... routes
   │  ├─ serializers.py
   │  └─ permissions.py
   ├─ base/                     # Domain models
   │  └─ models.py              # Event model
   └─ fixtures/
      └─ initial_data.json      # Sample events

Feature Summary
---------------
- CRUD for events with creator ownership checks and admin override.
- Student registration and unregistration with capacity-aware queries (full/available).
- Rich discovery: search by keyword, host, type, location, creator; date-based upcoming/past views.
- Sorting by creation, update, start, or end date to support different presentation needs.
- Aggregates and utilities: event counts, registered student lists, and multi-filter queries.
- Sample fixtures (``fixtures/initial_data.json``) for quick demos and manual testing.
