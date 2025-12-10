from rest_framework import viewsets
from apps.dependecias_municipales.models import DependenciaMunicipal
from apps.dependecias_municipales.serializers import DependenciaMunicipalSerializer


class DependenciaMunicipalViewSet(viewsets.ModelViewSet):
    queryset = DependenciaMunicipal.objects.all()
    serializer_class = DependenciaMunicipalSerializer
    pagination_class = None
