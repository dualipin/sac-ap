from django.db.models import Count, Q
from rest_framework import views, permissions

from apps.autenticacion.models import Usuario
from apps.utils.permissions import IsAdminOrFuncionario
from apps.solicitudes.models import Solicitud


class SolicitudAnaliticaView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        # Lógica para manejar la solicitud GET

        user: Usuario = request.user

        queryset = Solicitud.objects.filter(
            categoria__dependencia_municipal=user.funcionario.dependencia
        )

        data = queryset.aggregate(
            realizadas=Count('id'),
            aprobadas=Count('id', filter=Q(estado='completada')),
            rechazadas=Count('id', filter=Q(estado='rechazada')),
        )

        return views.Response(data)
