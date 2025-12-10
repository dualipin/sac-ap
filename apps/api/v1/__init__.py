from django.urls import path, include

urlpatterns = [
    path("analitica/", include("apps.api.v1.analitica")),
    path("localidades/", include("apps.api.v1.localidades")),
    path("ciudadanos/", include("apps.api.v1.ciudadanos")),
    path("token/", include("apps.api.v1.autenticacion")),
    path("programas/", include("apps.api.v1.programas")),
    path("solicitudes/", include("apps.api.v1.solicitudes")),
    path("notificaciones/", include("apps.api.v1.notificaciones")),
    path("dependencias/", include("apps.api.v1.dependecias_municipales")),
]
