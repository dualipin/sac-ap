from rest_framework import permissions
from rest_framework.request import Request

from apps.autenticacion.models import Usuario
from apps.autenticacion.constants import ADMIN, FUNCIONARIO, CIUDADANO


class IsAdmin(permissions.BasePermission):
    """
    Permiso de solo administradores.
    Valida que el usuario tenga rol 'admin'.
    """

    def has_permission(self, request: Request, view):
        user: Usuario = request.user

        return bool(user and user.is_authenticated and user.rol == ADMIN)


class IsFuncionario(permissions.BasePermission):
    """
    Permiso de solo funcionarios.
    """

    def has_permission(self, request: Request, view):
        user: Usuario = request.user

        return bool(user and user.is_authenticated and user.rol == FUNCIONARIO)


class IsCiudadano(permissions.BasePermission):
    """
    Permiso de solo ciudadanos.
    """

    def has_permission(self, request: Request, view):
        user: Usuario = request.user

        return bool(user and user.is_authenticated and user.rol == CIUDADANO)


class IsAdminOrFuncionario(permissions.BasePermission):
    """
    Permiso de administradores o funcionarios.
    """

    def has_permission(self, request: Request, view):
        user: Usuario = request.user

        return bool(user and user.is_authenticated and user.rol in [ADMIN, FUNCIONARIO])
