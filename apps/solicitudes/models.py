from django.db import models
from django.core.validators import FileExtensionValidator
from django_softdelete.models import SoftDeleteModel

from apps.ciudadanos.models import Ciudadano
from apps.dependecias_municipales.models import DependenciaMunicipal


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    dependencia_municipal = models.ForeignKey(
        DependenciaMunicipal, on_delete=models.PROTECT, related_name="categorias"
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def puede_eliminarse(self):
        """Verifica si la categoría puede ser eliminada (no tiene solicitudes activas)"""
        return not self.solicitudes.filter(estado__in=["enviada", "visto"]).exists()


class Solicitud(SoftDeleteModel):
    ESTADOS_CHOICES = [
        ("enviada", "Enviada"),
        ("visto", "Visto"),
        ("completada", "Completada"),
        ("rechazada", "Rechazada"),
    ]

    folio = models.CharField(max_length=100, unique=True, db_index=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="solicitudes"
    )
    descripcion = models.TextField()
    archivo_adjunto = models.FileField(
        upload_to="adjuntos/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "jpg", "jpeg", "png"]
            )
        ],
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_index=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(
        max_length=20, choices=ESTADOS_CHOICES, default="enviada", db_index=True
    )
    ciudadano = models.ForeignKey(
        Ciudadano,
        on_delete=models.CASCADE,
        related_name="solicitudes",
    )

    class Meta:
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["ciudadano", "-fecha_creacion"]),
            models.Index(fields=["estado", "-fecha_creacion"]),
        ]

    def __str__(self):
        return f"{self.folio} - {self.ciudadano.nombre_completo}"


class Comentario(models.Model):
    solicitud = models.ForeignKey(
        Solicitud, on_delete=models.CASCADE, related_name="comentarios"
    )
    texto = models.TextField()
    archivo_adjunto = models.FileField(
        upload_to="comentarios/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "jpg", "jpeg", "png"]
            )
        ],
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.CharField(
        max_length=100, default="Sistema"
    )  # Nombre de quien crea el comentario

    class Meta:
        ordering = ["fecha_creacion"]
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"

    def __str__(self):
        return f"Comentario en {self.solicitud.folio} - {self.fecha_creacion}"
