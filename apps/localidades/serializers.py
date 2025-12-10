from rest_framework import serializers
from .models import Localidad


class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = ['id', 'codigo_postal', 'colonia', 'municipio', 'estado', 'tipo']
