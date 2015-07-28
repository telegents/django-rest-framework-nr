from rest_framework import permissions
from libs.funcs import getattr_str


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view, obj=None):
        return request.user.is_superuser


class DomainPermission(permissions.BasePermission):
    """
    Checks if user has permission to the object based on domain access
    """

    def _user_has_domain_access(self, user, domain, access=None):
        if user.is_superuser:
            return True

        if not domain:
            return False

        access = access or ['admin']
        try:
            user.domainuser_set.get(
                domain=domain,
                domain__enabled=True,
                access__in=access,
                )
            return True
        except:
            return False

    def _domain_from_path(self, obj, path):
        if path == 'self':
            return obj

        try:
            return getattr_str(obj, path)
        except:
            return None
