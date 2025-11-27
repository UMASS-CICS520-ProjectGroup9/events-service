API Endpoints (``/api/``)
=========================

Base URL: ``/api/``

Core
----
- ``GET /api/`` — overview of key routes.
- ``GET /api/events/`` — list all events (ordered by end date).
- ``GET /api/events/<eventID>/`` — retrieve a single event by ID.
- ``GET /api/events/<creator_id>/creator_id/`` — events created by the given user (student/staff/admin).

Mutations
---------
- ``POST /api/events/create/`` — create an event; ``creator_id`` inferred from the authenticated user.
- ``PUT /api/events/<eventID>/update/`` — update an event (owner or admin).
- ``DELETE /api/events/<eventID>/delete/`` — delete an event (owner or admin).
- ``POST /api/events/<eventID>/register/`` — register a student; body requires ``student_id``.
- ``POST /api/events/<eventID>/unregister/`` — unregister a student; body requires ``student_id``.

Registration Utilities
----------------------
- ``GET /api/events/<eventID>/registered_students/`` — list registered students.
- ``GET /api/events/full/`` — events at or over capacity.
- ``GET /api/events/available/`` — events with available seats.

Sorting and Counting
--------------------
- ``GET /api/events/sorted_by_creation_date/``
- ``GET /api/events/sorted_by_update_date/``
- ``GET /api/events/sorted_by_start_date/``
- ``GET /api/events/sorted_by_end_date/``
- ``GET /api/events/count/`` — total number of events.

Date Views
----------
- ``GET /api/events/upcoming/`` — events whose start date is in the future.
- ``GET /api/events/past/`` — events whose end date has passed.
- ``GET /api/events/by_date_range/?start_date=&end_date=`` — events whose window falls within a range (ISO timestamps).
- ``GET /api/events/recent/<days>/`` — events created in the last ``days`` days.

Filtering and Search
--------------------
- ``GET /api/events/search/?q=<text>`` — search title/description.
- ``GET /api/events/by_host/<hosted_by>/``
- ``GET /api/events/by_type/<eventType>/``
- ``GET /api/events/by_location/<location>/``
- ``GET /api/events/by_creator/<creator>/``
- ``GET /api/events/by_capacity/<min_capacity>/`` — minimum capacity filter.
- ``GET /api/events/by_keyword/?keyword=<text>`` — keyword match in title/description.
- ``GET /api/events/filters/?creator=&eventType=&location=&host=&min_capacity=&max_capacity=`` — multi-criteria filtering.

Links
-----
- ``GET /api/events/with_links/`` — events with non-empty links.
- ``GET /api/events/with_zoom_links/`` — events with non-empty Zoom links.

Meta
----
- ``GET /api/health/`` — health check.
- ``GET /api/info/`` — service metadata.
- ``GET /api/welcome/`` — welcome message.
