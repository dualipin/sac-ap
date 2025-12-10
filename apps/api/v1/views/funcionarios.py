from rest_framework import generics, permissions
from apps.cuentas.models.funcionario import Funcionario
from apps.cuentas.serializers.funcionario_serializer import FuncionarioSerializer
from apps.utils.permissions import IsAdmin


class FuncionarioListCreate(generics.ListCreateAPIView):
    """
    Endpoint para listar y crear funcionarios
    Acceso: Solo administradores
    """

    permission_classes = [IsAdmin]
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer
