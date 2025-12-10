from django.db import models
from django_softdelete.models import SoftDeleteModel
from apps.dependecias_municipales.models import DependenciaMunicipal


class Programa(SoftDeleteModel):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    requisitos = models.JSONField(default=dict)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    dependencia_municipal = models.ForeignKey(
        DependenciaMunicipal,
        on_delete=models.CASCADE,
        related_name='programas'
    )

    def __str__(self):
        return self.titulo
