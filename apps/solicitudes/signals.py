from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.solicitudes.models import Solicitud, Comentario
from apps.solicitudes.notificaciones import Notificacion


@receiver(post_save, sender=Solicitud)
def crear_notificacion_solicitud(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando se crea o actualiza una solicitud
    """
    if created:
        # Nueva solicitud creada
        Notificacion.objects.create(
            solicitud=instance,
            ciudadano=instance.ciudadano,
            tipo="solicitud_creada",
            mensaje=f'Tu solicitud "{instance.folio}" ha sido registrada exitosamente.',
        )
    else:
        # Solicitud actualizada - crear notificación según el estado
        if instance.estado == "completada":
            Notificacion.objects.create(
                solicitud=instance,
                ciudadano=instance.ciudadano,
                tipo="solicitud_completada",
                mensaje=f'Tu solicitud "{instance.folio}" ha sido completada.',
            )
        elif instance.estado == "rechazada":
            Notificacion.objects.create(
                solicitud=instance,
                ciudadano=instance.ciudadano,
                tipo="solicitud_rechazada",
                mensaje=f'Tu solicitud "{instance.folio}" ha sido rechazada. Revisa los comentarios para más detalles.',
            )
        elif instance.estado == "visto":
            Notificacion.objects.create(
                solicitud=instance,
                ciudadano=instance.ciudadano,
                tipo="solicitud_actualizada",
                mensaje=f'Tu solicitud "{instance.folio}" está siendo revisada.',
            )


@receiver(post_save, sender=Comentario)
def crear_notificacion_comentario(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando se añade un comentario a una solicitud
    """
    if created:
        Notificacion.objects.create(
            solicitud=instance.solicitud,
            ciudadano=instance.solicitud.ciudadano,
            tipo="comentario_nuevo",
            mensaje=f'Hay un nuevo comentario en tu solicitud "{instance.solicitud.folio}".',
        )


# Registrar los signals cuando se importe este módulo
def ready():
    """Esta función se llama cuando la app está lista"""
    pass
