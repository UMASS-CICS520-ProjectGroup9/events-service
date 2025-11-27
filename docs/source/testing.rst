Testing
=======

Pytest Suite
------------
- Run all tests (preferred)::

    pytest

- Run a subset::

    pytest eventsService/api/tests/test_api_endpoints.py

Django Test Runner
------------------
- Standard Django runner remains available::

    cd eventsService
    python manage.py test

Sanity Checks
-------------
- Validate configuration without hitting the database::

    python manage.py check
