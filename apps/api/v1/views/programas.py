from rest_framework import generics, viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.programas.models import Programa
from apps.programas.serializers import (
    ProgramaSerializer,
    ListarProgramaSerializer,
    RegistrarProgramaSerializer,
)
from apps.utils.permissions import IsAdmin, IsFuncionario


class ProgramasListView(generics.ListAPIView):
    queryset = Programa.objects.all().order_by("-fecha_creacion")
    serializer_class = ListarProgramaSerializer
    permission_classes = [permissions.AllowAny]


class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = Programa.objects.all().order_by("-fecha_creacion")
    serializer_class = ProgramaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """Permisos por acción.

        Escritura permitida a admin y funcionario (con validación adicional
        en perform_create/update/destroy). Lectura para cualquier autenticado.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdmin() | IsFuncionario()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return Programa.objects.all().order_by("-fecha_creacion")

        if getattr(user, "rol", None) == "funcionario":
            try:
                dependencia = user.funcionario.dependencia
                return Programa.objects.filter(
                    dependencia_municipal=dependencia
                ).order_by("-fecha_creacion")
            except Exception:
                return Programa.objects.none()

        # Otros roles: solo lectura general (si se desea filtrar más, ajustar aquí)
        return Programa.objects.all().order_by("-fecha_creacion")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RegistrarProgramaSerializer
        return ProgramaSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            serializer.save()
            return

        if getattr(user, "rol", None) == "funcionario":
            try:
                dependencia = user.funcionario.dependencia
            except Exception:
                raise PermissionDenied("Funcionario no encontrado")

            # Forzamos la dependencia del funcionario, ignorando payload arbitrario
            serializer.save(dependencia_municipal=dependencia)
            return

        raise PermissionDenied("Rol no autorizado para registrar programas")

    def perform_update(self, serializer):
        user = self.request.user
        programa = self.get_object()

        if getattr(user, "rol", None) == "admin":
            serializer.save()
            return

        if getattr(user, "rol", None) == "funcionario":
            try:
                dependencia = user.funcionario.dependencia
            except Exception:
                raise PermissionDenied("Funcionario no encontrado")

            if programa.dependencia_municipal != dependencia:
                raise PermissionDenied("Solo puede editar programas de su dependencia")

            # No permitir cambiar dependencia
            serializer.save(dependencia_municipal=dependencia)
            return

        raise PermissionDenied("Rol no autorizado para editar programas")

    def destroy(self, request, *args, **kwargs):
        user = request.user
        programa = self.get_object()

        if getattr(user, "rol", None) == "admin":
            return super().destroy(request, *args, **kwargs)

        if getattr(user, "rol", None) == "funcionario":
            try:
                dependencia = user.funcionario.dependencia
            except Exception:
                raise PermissionDenied("Funcionario no encontrado")

            if programa.dependencia_municipal != dependencia:
                raise PermissionDenied(
                    "Solo puede eliminar programas de su dependencia"
                )

            return super().destroy(request, *args, **kwargs)

        raise PermissionDenied("Rol no autorizado para eliminar programas")
