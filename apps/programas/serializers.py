from rest_framework import serializers
from .models import Programa
from apps.dependecias_municipales.models import DependenciaMunicipal


class RegistrarProgramaSerializer(serializers.ModelSerializer):
    dependencia_municipal = serializers.PrimaryKeyRelatedField(
        queryset=DependenciaMunicipal.objects.all()
    )

    class Meta:
        model = Programa
        fields = ["titulo", "descripcion", "requisitos", "dependencia_municipal"]


class ListarProgramaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Programa
        fields = [
            "id",
            "titulo",
            "descripcion",
            "requisitos",
            "fecha_creacion",
            "dependencia_municipal",
        ]
        depth = 1


class ProgramaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    dependencia_municipal = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Programa
        fields = [
            "id",
            "titulo",
            "descripcion",
            "requisitos",
            "fecha_creacion",
            "dependencia_municipal",
        ]
