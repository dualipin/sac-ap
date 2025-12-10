from django.db import models


class Localidad(models.Model):
    """
    Modelo Localidad, los datos son los que proporciona el INEGI
    """
    codigo_postal = models.CharField(max_length=5, db_index=True, )
    colonia = models.CharField(max_length=255, db_column='col', )
    municipio = models.CharField(max_length=255, db_column='mun', )
    estado = models.CharField(max_length=100, db_column='est', )
    tipo = models.CharField(max_length=100, db_column='tp', )

    class Meta:
        verbose_name = 'Localidad'
        verbose_name_plural = 'Localidades'

    def __str__(self):
        return f"{self.colonia}, {self.municipio}, {self.estado}, CP: {self.codigo_postal}"
