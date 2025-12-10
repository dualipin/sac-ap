from django.db import models
from apps.autenticacion.models import Usuario
from apps.localidades.models import Localidad


class Ciudadano(models.Model):
    curp = models.CharField(max_length=18, unique=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name='ciudadanos')
    calle = models.CharField(max_length=100)
    numero_exterior = models.CharField(max_length=10)
    numero_interior = models.CharField(max_length=10, blank=True, null=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.PROTECT)
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], default='O')

    @property
    def nombre_completo(self):
        if self.apellido_materno:
            return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
        return f"{self.nombre} {self.apellido_paterno}"
