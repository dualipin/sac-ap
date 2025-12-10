from rest_framework import generics, permissions
from apps.cuentas.models.dependencia import Dependencia
from apps.cuentas.serializers.dependencia_serializer import DependenciaSerializer


class DependenciaListCreate(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Dependencia.objects.all()
    serializer_class = DependenciaSerializer
