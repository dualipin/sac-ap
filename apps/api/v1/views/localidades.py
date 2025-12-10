from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from apps.localidades.models import Localidad
from apps.localidades.serializers import LocalidadSerializer


class LocalidadApiView(ListAPIView):
    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['codigo_postal']
    permission_classes = []
    authentication_classes = []

    def get_queryset(self):
        queryset = Localidad.objects.all()

        assert isinstance(self.request, Request)
        codigo_postal = self.request.query_params.get('codigo_postal', None)

        if not codigo_postal:
            raise ValidationError({'detail': 'El parámetro codigo_postal es obligatorio.'})

        return queryset
