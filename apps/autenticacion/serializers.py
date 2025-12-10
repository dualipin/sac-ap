from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from apps.autenticacion.models import Usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: Usuario) -> Token:
        token = super().get_token(user)

        token["rol"] = user.rol

        # Si es funcionario, agregar su ID y dependencia
        if user.rol == "funcionario" and hasattr(user, "funcionario"):
            token["funcionario_id"] = user.funcionario.id
            token["dependencia_id"] = user.funcionario.dependencia.id

        return token
