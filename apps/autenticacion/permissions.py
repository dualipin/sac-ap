from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdmin(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'admin'.
    Busca por 'admin' en lugar de 'administrador'.
    """

    message = "Solo administradores pueden acceder a este recurso."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == "admin"
        )


class IsFuncionario(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'funcionario'.
    """

    message = "Solo funcionarios pueden acceder a este recurso."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == "funcionario"
        )


class IsCiudadano(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'ciudadano'.
    """

    message = "Solo ciudadanos pueden acceder a este recurso."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == "ciudadano"
        )


class IsAdminOrFuncionario(BasePermission):
    """
    Permite acceso a usuarios con rol 'admin' o 'funcionario'.
    """

    message = "Solo administradores y funcionarios pueden acceder a este recurso."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol in ["admin", "funcionario"]
        )
