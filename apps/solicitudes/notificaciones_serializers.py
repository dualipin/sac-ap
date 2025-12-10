from rest_framework import serializers
from apps.solicitudes.notificaciones import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""

    folio_solicitud = serializers.CharField(source="solicitud.folio", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Notificacion
        fields = [
            "id",
            "tipo",
            "tipo_display",
            "mensaje",
            "folio_solicitud",
            "leida",
            "fecha_creacion",
            "fecha_lectura",
        ]
        read_only_fields = [
            "id",
            "tipo",
            "tipo_display",
            "mensaje",
            "folio_solicitud",
            "fecha_creacion",
            "fecha_lectura",
        ]
