from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.funcionarios.models import Funcionario
from apps.funcionarios.serializers import RegistrarFuncionario
from apps.utils.permissions import IsAdmin


class FuncionarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar funcionarios.
    - list, retrieve: Cualquier usuario autenticado puede ver
    - create, update, partial_update, destroy: Solo administradores
    """

    queryset = Funcionario.objects.select_related("dependencia", "usuario").all()
    serializer_class = RegistrarFuncionario
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Asigna permisos según la acción:
        - list, retrieve: IsAuthenticated
        - create, update, partial_update, destroy: IsAdmin
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        Lista todos los funcionarios con sus dependencias.
        """
        funcionarios = self.get_queryset()

        data = []
        for func in funcionarios:
            data.append(
                {
                    "id": func.id,
                    "nombre_completo": func.nombre_completo,
                    "correo": func.correo,
                    "telefono": func.telefono,
                    "cargo": func.cargo,
                    "sexo": func.sexo,
                    "dependencia": (
                        {
                            "id": func.dependencia.id,
                            "nombre": func.dependencia.nombre,
                        }
                        if func.dependencia
                        else None
                    ),
                    "usuario": (
                        {
                            "id": func.usuario.id,
                            "correo": func.usuario.usuario,
                        }
                        if func.usuario
                        else None
                    ),
                }
            )

        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """
        Obtiene los detalles de un funcionario.
        """
        instance = self.get_object()
        data = {
            "id": instance.id,
            "nombre_completo": instance.nombre_completo,
            "correo": instance.correo,
            "telefono": instance.telefono,
            "cargo": instance.cargo,
            "sexo": instance.sexo,
            "dependencia": (
                {
                    "id": instance.dependencia.id,
                    "nombre": instance.dependencia.nombre,
                }
                if instance.dependencia
                else None
            ),
            "usuario": (
                {
                    "id": instance.usuario.id,
                    "correo": instance.usuario.usuario,
                }
                if instance.usuario
                else None
            ),
        }
        return Response(data)

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo funcionario con su usuario asociado.
        Solo administradores pueden crear.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        funcionario = serializer.instance
        return Response(
            {
                "id": funcionario.id,
                "nombre_completo": funcionario.nombre_completo,
                "correo": funcionario.correo,
                "telefono": funcionario.telefono,
                "cargo": funcionario.cargo,
                "sexo": funcionario.sexo,
                "dependencia": (
                    {
                        "id": funcionario.dependencia.id,
                        "nombre": funcionario.dependencia.nombre,
                    }
                    if funcionario.dependencia
                    else None
                ),
                "usuario": (
                    {
                        "id": funcionario.usuario.id,
                        "correo": funcionario.usuario.usuario,
                    }
                    if funcionario.usuario
                    else None
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        Actualiza un funcionario existente.
        Solo administradores pueden actualizar.
        """
        instance = self.get_object()
        partial = kwargs.pop("partial", False)

        # Campos actualizables
        updateable_fields = {
            "nombre_completo": "nombre_completo",
            "telefono": "telefono",
            "cargo": "cargo",
            "sexo": "sexo",
            "dependencia": "dependencia",
        }

        for field, attr in updateable_fields.items():
            if field in request.data:
                setattr(instance, attr, request.data[field])

        instance.save()
        return self.retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un funcionario y su usuario asociado.
        Solo administradores pueden eliminar.
        """
        instance = self.get_object()
        usuario = instance.usuario
        instance.delete()

        # Eliminar usuario asociado si existe
        if usuario:
            usuario.delete()

        return Response(
            {"detail": "Funcionario eliminado correctamente"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def por_dependencia(self, request):
        """
        Lista funcionarios agrupados por dependencia.
        GET /api/v1/funcionarios/por_dependencia/
        """
        from django.db.models import Count
        from apps.dependecias_municipales.models import DependenciaMunicipal

        dependencias = (
            DependenciaMunicipal.objects.annotate(
                num_funcionarios=Count("funcionarios")
            )
            .prefetch_related("funcionarios")
            .filter(num_funcionarios__gt=0)
        )

        data = []
        for dep in dependencias:
            data.append(
                {
                    "dependencia": {
                        "id": dep.id,
                        "nombre": dep.nombre,
                    },
                    "funcionarios": [
                        {
                            "id": func.id,
                            "nombre_completo": func.nombre_completo,
                            "correo": func.correo,
                            "cargo": func.cargo,
                        }
                        for func in dep.funcionarios.all()
                    ],
                    "total": dep.num_funcionarios,
                }
            )

        return Response(data)
