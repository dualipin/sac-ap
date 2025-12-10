from django.db import models
from apps.ciudadanos.models import Ciudadano
from apps.solicitudes.models import Solicitud


class Notificacion(models.Model):
    """
    Modelo para almacenar notificaciones de cambios en solicitudes
    """

    TIPOS_CHOICES = [
        ("solicitud_creada", "Solicitud Creada"),
        ("solicitud_actualizada", "Solicitud Actualizada"),
        ("solicitud_completada", "Solicitud Completada"),
        ("solicitud_rechazada", "Solicitud Rechazada"),
        ("comentario_nuevo", "Nuevo Comentario"),
    ]

    solicitud = models.ForeignKey(
        Solicitud, on_delete=models.CASCADE, related_name="notificaciones"
    )
    ciudadano = models.ForeignKey(
        Ciudadano, on_delete=models.CASCADE, related_name="notificaciones"
    )
    tipo = models.CharField(
        max_length=30, choices=TIPOS_CHOICES, default="solicitud_actualizada"
    )
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["ciudadano", "-fecha_creacion"]),
            models.Index(fields=["leida"]),
        ]
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"Notificación para {self.ciudadano.nombre_completo} - {self.get_tipo_display()}"

    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        from django.utils import timezone

        self.leida = True
        self.fecha_lectura = timezone.now()
        self.save()
