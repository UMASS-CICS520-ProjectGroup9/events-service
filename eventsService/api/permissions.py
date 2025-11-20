from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "ADMIN"

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return (request.user.role == "STUDENT") or (request.user.role == "ADMIN") or (request.user.role == "STAFF")

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return (request.user.role == "STAFF") or (request.user.role == "ADMIN") 

class IsOwnerOrAdmin(BasePermission):
    """
    User can modify their own events.
    Admin can modify anything.
    """

    def has_object_permission(self, request, view, obj):
        # Optional: allow read for everyone who passes has_permission
        if request.method in SAFE_METHODS:
            return True

        # Write permissions: only owner or admin
        is_owner = (obj.creator_id == request.user.id)
        is_admin = getattr(request.user, "role", "").upper() == "ADMIN"
        return is_owner or is_admin
        