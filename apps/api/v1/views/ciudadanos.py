import datetime

from rest_framework import generics, permissions, views, status
from apps.ciudadanos.models import Ciudadano
from apps.ciudadanos.serializers import RegistroCiudadanoSerializer


class RegistrarCiudadanoCreateView(generics.CreateAPIView):
    """
    Endpoint para registrar un nuevo ciudadano
    Acceso público (sin autenticación requerida)
    """

    queryset = Ciudadano.objects.all()
    serializer_class = RegistroCiudadanoSerializer
    permission_classes = [permissions.AllowAny]


class VerificarCiudadanoRegistradoView(views.APIView):
    """
    Endpoint para verificar si un ciudadano está registrado por CURP
    Acceso público (sin autenticación requerida)
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, curp: str):
        curp = curp.upper()

        registrado = {
            "registrado": False,
            "mensaje": "No se encontró ningún ciudadano con el CURP proporcionado.",
        }

        try:
            ciudadano = Ciudadano.objects.get(curp__iexact=curp)

            registrado["registrado"] = True
            registrado["mensaje"] = "El ciudadano está registrado."

            return views.Response(registrado, status=status.HTTP_200_OK)
        except Ciudadano.DoesNotExist:
            return views.Response(registrado, status=status.HTTP_404_NOT_FOUND)
