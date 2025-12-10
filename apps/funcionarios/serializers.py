from rest_framework import serializers
from .models import Funcionario
from ..autenticacion.models import Usuario


class RegistrarFuncionario(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        try:
            usuario = Usuario.objects.create_user(
                usuario=validated_data['correo'],
                rol='funcionario',
                password=validated_data['password'],
            )

        except Exception as e:
            raise serializers.ValidationError(f"Error al crear el usuario: {str(e)}")

        funcionario = Funcionario(
            nombre_completo=validated_data['nombre_completo'],
            correo=validated_data['correo'],
            telefono=validated_data['telefono'],
            cargo=validated_data['cargo'],
            dependencia=validated_data['dependencia'],
            usuario=usuario,
        )
        funcionario.save()
        return funcionario

    class Meta:
        model = Funcionario
        fields = [
            'nombre_completo',
            'correo',
            'telefono',
            'cargo',
            'dependencia',
            'password'
        ]
