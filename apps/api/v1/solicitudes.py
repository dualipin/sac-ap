from django.urls import path
from rest_framework import routers

from apps.api.v1.views.solicitudes import CategoriasListView, SolicitudViewSet

router = routers.DefaultRouter()
router.register(r"categorias", CategoriasListView, basename="categoria")
router.register(r"", SolicitudViewSet, basename="solicitud")

urlpatterns = [] + router.urls
