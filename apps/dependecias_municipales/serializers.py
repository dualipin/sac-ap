from rest_framework import serializers
from .models import DependenciaMunicipal


class DependenciaMunicipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DependenciaMunicipal
        fields = ['id', 'nombre', 'descripcion']
