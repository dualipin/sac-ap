from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from apps.solicitudes.notificaciones import Notificacion
from apps.solicitudes.notificaciones_serializers import NotificacionSerializer
from apps.utils.permissions import IsCiudadano


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestionar notificaciones del ciudadano
    Los ciudadanos solo pueden ver sus propias notificaciones
    """

    serializer_class = NotificacionSerializer
    permission_classes = [IsCiudadano]

    def get_queryset(self):
        """Retorna solo las notificaciones del ciudadano autenticado"""
        try:
            ciudadano = self.request.user.ciudadano
            return Notificacion.objects.filter(ciudadano=ciudadano)
        except:
            return Notificacion.objects.none()

    @action(detail=False, methods=["get"])
    def no_leidas(self, request: Request):
        """Obtener solo notificaciones no leídas"""
        try:
            ciudadano = request.user.ciudadano
            notificaciones = Notificacion.objects.filter(
                ciudadano=ciudadano, leida=False
            )
            serializer = self.get_serializer(notificaciones, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {"detail": "Ciudadano no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"])
    def marcar_como_leida(self, request: Request, pk=None):
        """Marcar una notificación como leída"""
        notificacion = self.get_object()

        # Validar que pertenece al ciudadano autenticado
        try:
            if notificacion.ciudadano != request.user.ciudadano:
                return Response(
                    {"detail": "No tiene permiso para marcar esta notificación"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except:
            return Response(
                {"detail": "Acceso denegado"}, status=status.HTTP_403_FORBIDDEN
            )

        notificacion.marcar_como_leida()
        serializer = self.get_serializer(notificacion)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def marcar_todas_como_leidas(self, request: Request):
        """Marcar todas las notificaciones como leídas"""
        try:
            ciudadano = request.user.ciudadano
            notificaciones = Notificacion.objects.filter(
                ciudadano=ciudadano, leida=False
            )

            for notificacion in notificaciones:
                notificacion.marcar_como_leida()

            return Response(
                {
                    "detail": f"{notificaciones.count()} notificaciones marcadas como leídas"
                }
            )
        except:
            return Response(
                {"detail": "Ciudadano no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"])
    def no_leidas_count(self, request: Request):
        """Obtener el conteo de notificaciones no leídas"""
        try:
            ciudadano = request.user.ciudadano
            count = Notificacion.objects.filter(
                ciudadano=ciudadano, leida=False
            ).count()
            return Response({"no_leidas": count})
        except:
            return Response(
                {"detail": "Ciudadano no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
