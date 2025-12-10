from rest_framework import serializers
from apps.utils.validation.curp import validar_curp
from .models import Ciudadano
from ..autenticacion.models import Usuario


class RegistroCiudadanoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate_curp(self, value: str):
        value = value.upper().strip()

        if not validar_curp(value):
            raise serializers.ValidationError("El CURP proporcionado no es válido.")

        ciudadano = self.Meta.model.objects.filter(curp__iexact=value)

        if ciudadano:
            raise serializers.ValidationError("El CURP ya está registrado.")

        return value

    def create(self, validated_data):
        usuario = Usuario.objects.create_user(
            usuario=validated_data['curp'],
            rol='ciudadano',
            password=validated_data['password'],
        )

        ciudadano = self.Meta.model.objects.create(
            curp=validated_data['curp'],
            nombre=validated_data['nombre'],
            apellido_paterno=validated_data['apellido_paterno'],
            apellido_materno=validated_data['apellido_materno'],
            fecha_nacimiento=validated_data['fecha_nacimiento'],
            localidad=validated_data['localidad'],
            calle=validated_data['calle'],
            numero_exterior=validated_data['numero_exterior'],
            numero_interior=validated_data.get('numero_interior', ''),
            usuario=usuario,
        )

        return ciudadano

    class Meta:
        model = Ciudadano
        fields = [
            'curp',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'fecha_nacimiento',
            'localidad',
            'calle',
            'numero_exterior',
            'numero_interior',
            'password',
        ]
