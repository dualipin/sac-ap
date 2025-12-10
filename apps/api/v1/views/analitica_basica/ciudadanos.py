from django.db.models import Count, Q
from rest_framework import views, permissions

from apps.autenticacion.models import Usuario
from apps.utils.permissions import IsCiudadano
from apps.solicitudes.models import Solicitud


class SolicitudesCiudadanosView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, IsCiudadano)

    def get(self, request: views.Request, *args, **kwargs):
        # Lógica para manejar la solicitud GET

        user: Usuario = request.user

        queryset = Solicitud.objects.filter(ciudadano=user.ciudadano)

        data = queryset.aggregate(
            realizadas=Count('id'),
            aprobadas=Count('id', filter=Q(estado='completada')),
            rechazadas=Count('id', filter=Q(estado='rechazada')),
        )

        return views.Response(data)
