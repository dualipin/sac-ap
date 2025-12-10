from django.db import models
from apps.autenticacion.models import Usuario
from apps.dependecias_municipales.models import DependenciaMunicipal


class Funcionario(models.Model):
    SEXO_CHOICES = [
        ("M", "Masculino"),
        ("F", "Femenino"),
    ]

    nombre_completo = models.CharField(max_length=200)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    cargo = models.CharField(max_length=100)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    dependencia = models.ForeignKey(DependenciaMunicipal, on_delete=models.CASCADE, related_name='funcionarios')
    usuario = models.OneToOneField(Usuario, on_delete=models.PROTECT, related_name='funcionario', null=True, blank=True)
