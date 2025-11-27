# Events Service API

Lightweight Django REST API for creating, updating, browsing, and registering for UMASS events. The service exposes a JSON-first `/api/` surface, uses JWT authentication shared with the user-auth service, and ships with sample data to get started quickly.

## Overview
- Built with Django 5 + Django REST Framework; ships with SQLite for local development.
- JWT-based auth via `ExternalJWTAuthentication` with role-aware permissions (student/staff/admin).
- Core domain: `Event` records with capacity, registration roster, schedule, hosting details, and links.
- Filtering, searching, sorting, and capacity-aware queries to support multiple event discovery flows.

## How to Compile and Run
1. From the repo root, create/activate a virtualenv (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\\Scripts\\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations and (optionally) load the sample data:
   ```bash
   cd eventsService
   python manage.py migrate
   python manage.py loaddata fixtures/initial_data.json  # optional seed data
   ```
4. Start the API:
   ```bash
   python manage.py runserver
   ```
5. Visit `http://localhost:8000/api/` to confirm the API is reachable.

## Python Version and Environment
- Use Python 3.10+ (aligned with Django 5.x requirements). A virtual environment is strongly recommended to isolate dependencies.
- Default settings use SQLite (`db.sqlite3`). For other databases, update `DATABASES` in `eventsService/settings.py`.
- JWT signing key defaults to the project secret; set `SIMPLE_JWT.SIGNING_KEY` (and `SECRET_KEY`) appropriately for non-local deployments.

## Features
- CRUD for events with creator ownership checks and admin override.
- Student registration and unregistration with capacity-aware queries (full/available).
- Rich discovery: search by keyword, host, type, location, creator; date-based upcoming/past views.
- Sorting by creation, update, start, or end date to support different presentation needs.
- Aggregates and utilities: event counts, registered student lists, and multi-filter queries.
- Sample fixtures (`fixtures/initial_data.json`) for quick demos and manual testing.

## Testing
- Run Django’s test suite from the project root:
  ```bash
  cd eventsService
  python manage.py test
  ```
- For a quick sanity check of the project configuration without hitting the DB, run `python manage.py check`.

## Project Structure
```
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
```

## Authentication
- Uses `Authorization: bearer <JWT>` headers decoded locally via `ExternalJWTAuthentication`.
- JWT payload must include `user_id`; optional `email`, `username`, and `role`.
- Role-aware permissions:
  - `IsStudent`: students, staff, and admins can create/update/delete/register.
  - `IsStaff`: staff and admins.
  - `IsAdmin`: admins only.
  - `IsOwnerOrAdmin`: only the event creator (matched by `creator_id`) or an admin can modify/delete.

## API Endpoints (`/api/`)
- `GET /api/` — simple overview of key routes.
- `GET /api/events/` — list all events (ordered by end date).
- `GET /api/events/<eventID>/` — retrieve a single event by ID.
- `GET /api/events/<creator_id>/creator_id/` — events created by the given user (student/staff/admin).
- `POST /api/events/create/` — create an event; `creator_id` is inferred from the authenticated user (student/staff/admin).
- `PUT /api/events/<eventID>/update/` — update an event (owner or admin).
- `DELETE /api/events/<eventID>/delete/` — delete an event (owner or admin).
- `POST /api/events/<eventID>/register/` — register a student; body requires `student_id`.
- `POST /api/events/<eventID>/unregister/` — unregister a student; body requires `student_id`.
- `GET /api/events/<eventID>/registered_students/` — list registered students for the event.
- `GET /api/events/full/` | `GET /api/events/available/` — events at capacity vs. with space.
- `GET /api/events/sorted_by_creation_date/` | `/sorted_by_update_date/` | `/sorted_by_start_date/` | `/sorted_by_end_date/` — sorted listings.
- `GET /api/events/count/` — total number of events.
- `GET /api/events/upcoming/` | `GET /api/events/past/` — date-based views using current time.
- `GET /api/events/search/?q=<text>` — search title/description.
- `GET /api/events/by_host/<hosted_by>/` | `/by_type/<eventType>/` | `/by_location/<location>/` | `/by_creator/<creator>/` — targeted filters.
- `GET /api/events/filters/?creator=&eventType=&location=&host=&min_capacity=&max_capacity=` — multi-criteria filtering.
