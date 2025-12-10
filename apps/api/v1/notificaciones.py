from django.urls import path
from rest_framework import routers

from apps.api.v1.views.notificaciones import NotificacionViewSet

router = routers.DefaultRouter()
router.register(r"", NotificacionViewSet, basename="notificacion")

urlpatterns = [] + router.urls
