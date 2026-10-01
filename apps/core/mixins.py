from django.core.exceptions import PermissionDenied


class RoleRequiredMixin:
    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.is_superuser or request.user.role in self.allowed_roles
        ):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied
