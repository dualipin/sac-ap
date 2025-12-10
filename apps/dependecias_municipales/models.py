from django.db import models


class DependenciaMunicipal(models.Model):
    TIPO_DEPENDENCIA_CHOICES = [
        ('coordinación', 'Coordinación'),
        ('dirección', 'Dirección'),
        ('subdirección', 'Subdirección'),
        ('departamento', 'Departamento'),
        ('otros', 'Otros'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=30, choices=TIPO_DEPENDENCIA_CHOICES, default='departamento')

    def __str__(self):
        return self.nombre
