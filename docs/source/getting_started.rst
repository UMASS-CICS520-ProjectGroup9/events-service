Getting Started
===============

Quick steps to run the Events Service locally.

Prerequisites
-------------
- Python 3.10+
- `pip` and `virtualenv` (recommended)

Setup
-----
1. Create and activate a virtual environment::

      python -m venv .venv
      source .venv/bin/activate  # on Windows: .venv\\Scripts\\activate

2. Install dependencies from the repo root::

      pip install -r requirements.txt

3. Apply migrations and (optionally) load sample data::

      cd eventsService
      python manage.py migrate
      python manage.py loaddata fixtures/initial_data.json  # optional seed data

4. Start the development server::

      python manage.py runserver

5. Verify the API is reachable at ``http://localhost:8000/api/``.

Configuration Notes
-------------------
- Database: SQLite by default (``db.sqlite3``). Update ``DATABASES`` in ``eventsService/settings.py`` to use Postgres or another backend.
- Secrets: The JWT signing key defaults to ``SIMPLE_JWT.SIGNING_KEY`` or ``SECRET_KEY``. Set both via environment variables for non-local deployments.
- Auth: Incoming requests must send ``Authorization: bearer <JWT>`` when endpoints require authentication.
