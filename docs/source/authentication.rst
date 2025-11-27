Authentication
==============

Scheme
------
- All protected endpoints expect ``Authorization: bearer <JWT>``.
- Tokens are decoded locally using ``ExternalJWTAuthentication`` with the shared signing key.

Token Payload
-------------
- Required: ``user_id`` (int).
- Optional: ``email``, ``username``, ``role``.
- Roles drive permissions:

  - ``IsStudent``: students, staff, and admins can create/update/delete/register.
  - ``IsStaff``: staff and admins.
  - ``IsAdmin``: admins only.
  - ``IsOwnerOrAdmin``: only the event creator (``creator_id``) or an admin can modify/delete.

Configuration
-------------
- Signing key: ``SIMPLE_JWT.SIGNING_KEY`` (falls back to ``SECRET_KEY``).
- Algorithm: ``SIMPLE_JWT.ALGORITHM`` (default ``HS256``).

Example Header
--------------
::

   Authorization: bearer <your-jwt-token>
