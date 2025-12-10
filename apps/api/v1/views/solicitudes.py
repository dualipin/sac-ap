import uuid

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.solicitudes.serializers import (
    CategoriasSerializer,
    ComentarioSerializer,
    RegistrarSolicitudSerializer,
    SolicitudSerializer,
    validate_attachment_size,
)
from apps.solicitudes.models import Categoria, Solicitud, Comentario
from apps.utils.permissions import IsFuncionario, IsCiudadano


class CategoriasListView(viewsets.ModelViewSet):
    serializer_class = CategoriasSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtra categorías según el rol del usuario:
        - Admin: ve todas las categorías
        - Funcionario: solo ve categorías de su dependencia
        - Ciudadano: ve todas las categorías
        """
        user = self.request.user

        if user.rol == "admin":
            return Categoria.objects.all()

        # Funcionarios ven solo categorías de su dependencia
        if user.rol == "funcionario":
            try:
                funcionario = user.funcionario
                return Categoria.objects.filter(
                    dependencia_municipal=funcionario.dependencia
                )
            except:
                return Categoria.objects.none()

        # Ciudadanos ven todas las categorías
        if user.rol == "ciudadano":
            return Categoria.objects.all()

        return Categoria.objects.none()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsFuncionario()]
        return [permissions.IsAuthenticated()]

    def create(self, request: Request, *args, **kwargs):
        """Crear categoría (solo funcionarios de la dependencia)"""
        if request.user.rol != "funcionario":
            return Response(
                {"detail": "Solo funcionarios pueden crear categorías"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            funcionario = request.user.funcionario
        except:
            return Response(
                {"detail": "Funcionario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validar que la dependencia en el request coincida con la del funcionario
        dependencia_id = request.data.get("dependencia_municipal")
        if int(dependencia_id) != funcionario.dependencia.id:
            return Response(
                {"detail": "Solo puede crear categorías para su propia dependencia"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

    def update(self, request: Request, *args, **kwargs):
        """Actualizar categoría (solo funcionarios de la dependencia)"""
        categoria = self.get_object()

        if request.user.rol != "funcionario":
            return Response(
                {"detail": "Solo funcionarios pueden actualizar categorías"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            funcionario = request.user.funcionario
            # Validar que la categoría pertenece a su dependencia
            if categoria.dependencia_municipal != funcionario.dependencia:
                return Response(
                    {"detail": "No puede actualizar categorías de otra dependencia"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except:
            return Response(
                {"detail": "Funcionario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request: Request, *args, **kwargs):
        """Actualizar parcial de categoría (solo funcionarios de la dependencia)"""
        categoria = self.get_object()

        if request.user.rol != "funcionario":
            return Response(
                {"detail": "Solo funcionarios pueden actualizar categorías"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            funcionario = request.user.funcionario
            # Validar que la categoría pertenece a su dependencia
            if categoria.dependencia_municipal != funcionario.dependencia:
                return Response(
                    {"detail": "No puede actualizar categorías de otra dependencia"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except:
            return Response(
                {"detail": "Funcionario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Eliminar categoría con validación"""
        categoria = self.get_object()

        if request.user.rol != "funcionario":
            return Response(
                {"detail": "Solo funcionarios pueden eliminar categorías"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            funcionario = request.user.funcionario
            if categoria.dependencia_municipal != funcionario.dependencia:
                return Response(
                    {"detail": "No puede eliminar categorías de otra dependencia"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except:
            return Response(
                {"detail": "Funcionario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not categoria.puede_eliminarse():
            return Response(
                {
                    "detail": "No se puede eliminar esta categoría porque tiene solicitudes activas"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


class SolicitudViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar solicitudes.
    - Ciudadanos pueden crear y ver sus propias solicitudes
    - Funcionarios pueden ver/actualizar solicitudes de su dependencia
    - Admin puede ver todas las solicitudes
    """

    serializer_class = SolicitudSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Retorna los permisos basados en la acción
        """
        if self.action in ["create"]:
            return [IsCiudadano()]
        elif self.action in ["update", "partial_update"]:
            return [IsFuncionario()]
        elif self.action in ["list", "retrieve", "detalles", "mis_solicitudes"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # Admin ve todo
        if user.rol == "admin":
            return Solicitud.objects.all()

        # Funcionario ve solicitudes de su dependencia
        if user.rol == "funcionario":
            try:
                funcionario = user.funcionario
                return Solicitud.objects.filter(
                    categoria__dependencia_municipal=funcionario.dependencia
                ).select_related("ciudadano", "categoria")
            except:
                return Solicitud.objects.none()

        # Ciudadano ve solo sus solicitudes
        if user.rol == "ciudadano":
            try:
                ciudadano = user.ciudadano
                return Solicitud.objects.filter(ciudadano=ciudadano)
            except:
                return Solicitud.objects.none()

        return Solicitud.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return RegistrarSolicitudSerializer
        return SolicitudSerializer

    def create(self, request: Request, *args, **kwargs):
        """Crear una nueva solicitud (solo ciudadanos)"""
        if request.user.rol != "ciudadano":
            return Response(
                {"detail": "Solo los ciudadanos pueden crear solicitudes"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ciudadano = request.user.ciudadano
        except:
            return Response(
                {"detail": "Ciudadano no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generar folio único
        folio = (
            f"SOL-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        )

        solicitud = Solicitud.objects.create(
            folio=folio,
            ciudadano=ciudadano,
            estado="enviada",
            **serializer.validated_data,
        )

        return Response(
            SolicitudSerializer(solicitud).data, status=status.HTTP_201_CREATED
        )

    def update(self, request: Request, *args, **kwargs):
        """Actualizar estado de solicitud (solo funcionarios de la dependencia)"""
        solicitud = self.get_object()

        # Validar que es funcionario
        if request.user.rol != "funcionario":
            return Response(
                {"detail": "Solo funcionarios pueden actualizar solicitudes"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            funcionario = request.user.funcionario
            # Validar que la solicitud pertenece a su dependencia
            if solicitud.categoria.dependencia_municipal != funcionario.dependencia:
                return Response(
                    {"detail": "No tiene permiso para actualizar esta solicitud"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except:
            return Response(
                {"detail": "Funcionario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Obtener nuevo estado del body
        nuevo_estado = request.data.get("estado")
        comentario_texto = request.data.get("comentario", "")
        archivo_adjunto = request.FILES.get("archivo_adjunto")

        if nuevo_estado and nuevo_estado not in dict(Solicitud.ESTADOS_CHOICES):
            return Response(
                {"estado": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST
            )

        if archivo_adjunto:
            validate_attachment_size(archivo_adjunto)

        if nuevo_estado:
            solicitud.estado = nuevo_estado
            solicitud.save()

        if comentario_texto or archivo_adjunto:
            texto = comentario_texto.strip() or "Archivo adjunto"

            try:
                Comentario.objects.create(
                    solicitud=solicitud,
                    texto=texto,
                    archivo_adjunto=archivo_adjunto,
                    creado_por=str(request.user),
                )
            except DjangoValidationError as exc:
                raise ValidationError(exc.message_dict or exc.messages)

        return Response(SolicitudSerializer(solicitud).data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def mis_solicitudes(self, request: Request):
        """Endpoint para listar solicitudes según rol.

        - Ciudadano: solo sus solicitudes
        - Funcionario: solicitudes de su dependencia
        - Admin: todas las solicitudes
        """

        user = request.user

        if user.rol == "ciudadano":
            try:
                ciudadano = user.ciudadano
                qs = Solicitud.objects.filter(ciudadano=ciudadano)
            except Exception:
                return Response(
                    {"detail": "Ciudadano no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif user.rol == "funcionario":
            try:
                funcionario = user.funcionario
                qs = Solicitud.objects.filter(
                    categoria__dependencia_municipal=funcionario.dependencia
                )
            except Exception:
                return Response(
                    {"detail": "Funcionario no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif user.rol == "admin":
            qs = Solicitud.objects.all()
        else:
            return Response(
                {"detail": "Rol no autorizado"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = SolicitudSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def detalles(self, request: Request, pk=None):
        """Obtener detalles completos de una solicitud con comentarios"""
        solicitud = self.get_object()

        # Validar acceso
        if request.user.rol == "ciudadano":
            try:
                if solicitud.ciudadano != request.user.ciudadano:
                    return Response(
                        {"detail": "No tiene permiso para ver esta solicitud"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except:
                return Response(
                    {"detail": "Acceso denegado"}, status=status.HTTP_403_FORBIDDEN
                )
        elif request.user.rol == "funcionario":
            try:
                if (
                    solicitud.categoria.dependencia_municipal
                    != request.user.funcionario.dependencia
                ):
                    return Response(
                        {"detail": "No tiene permiso para ver esta solicitud"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except:
                return Response(
                    {"detail": "Acceso denegado"}, status=status.HTTP_403_FORBIDDEN
                )

        data = SolicitudSerializer(solicitud, context={"request": request}).data
        data["comentarios"] = ComentarioSerializer(
            Comentario.objects.filter(solicitud=solicitud),
            many=True,
            context={"request": request},
        ).data

        return Response(data)
