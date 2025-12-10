from django.urls import path, include
from .views.analitica import (
    SesionStartView,
    SesionEndView,
    PaginaVistaBatchView,
    EventoBatchView,
    StatsSummaryView,
    DailyPageviewsView,
    TopPagesView,
    WebAnalyticsReportPDFView,
)
from .views.analitica_basica.ciudadanos import SolicitudesCiudadanosView
from .views.analitica_basica.funcionarios import (
    SolicitudAnaliticaView,
    EstadisticasCompletasView,
    SolicitudesPorPeriodoView,
    RankingFuncionariosView,
    MapaCalorGeograficoView,
    AlertasSolicitudesView,
    ComparacionPeriodosView,
    ReportePDFView,
    ExportarSolicitudesView,
)

analitica_basica_patterns = [
    path(
        "solicitudes-ciudadanos/",
        SolicitudesCiudadanosView.as_view(),
        name="solicitudes-ciudadanos",
    ),
    # Estadísticas para funcionarios
    path(
        "solicitudes-funcionarios/",
        SolicitudAnaliticaView.as_view(),
        name="solicitudes-funcionarios",
    ),
    path(
        "solicitudes-funcionarios/completas/",
        EstadisticasCompletasView.as_view(),
        name="solicitudes-funcionarios-completas",
    ),
    path(
        "solicitudes-funcionarios/periodo/",
        SolicitudesPorPeriodoView.as_view(),
        name="solicitudes-funcionarios-periodo",
    ),
    path(
        "solicitudes-funcionarios/ranking/",
        RankingFuncionariosView.as_view(),
        name="funcionarios-ranking",
    ),
    path(
        "solicitudes-funcionarios/mapa-calor/",
        MapaCalorGeograficoView.as_view(),
        name="solicitudes-mapa-calor",
    ),
    path(
        "solicitudes-funcionarios/alertas/",
        AlertasSolicitudesView.as_view(),
        name="solicitudes-alertas",
    ),
    path(
        "solicitudes-funcionarios/comparacion/",
        ComparacionPeriodosView.as_view(),
        name="solicitudes-comparacion",
    ),
    path(
        "solicitudes-funcionarios/reporte/pdf/",
        ReportePDFView.as_view(),
        name="solicitudes-reporte-pdf",
    ),
    path(
        "solicitudes-funcionarios/exportar/",
        ExportarSolicitudesView.as_view(),
        name="solicitudes-exportar",
    ),
]

urlpatterns = [
    path("sessions/start/", SesionStartView.as_view(), name="analytics-session-start"),
    path("sessions/end/", SesionEndView.as_view(), name="analytics-session-end"),
    path(
        "pageviews/batch/",
        PaginaVistaBatchView.as_view(),
        name="analytics-pageviews-batch",
    ),
    path("events/batch/", EventoBatchView.as_view(), name="analytics-events-batch"),
    # protected stats
    path("stats/summary/", StatsSummaryView.as_view(), name="analytics-stats-summary"),
    path(
        "stats/pageviews/daily/",
        DailyPageviewsView.as_view(),
        name="analytics-stats-daily",
    ),
    path("stats/pages/top/", TopPagesView.as_view(), name="analytics-top-pages"),
    path(
        "stats/report/pdf/",
        WebAnalyticsReportPDFView.as_view(),
        name="analytics-report-pdf",
    ),
    path("basica/", include(analitica_basica_patterns)),
]
