from datetime import timedelta
import csv
from django.db.models import (
    Count,
    Q,
    Avg,
    F,
    ExpressionWrapper,
    DurationField,
    Max,
    Min,
)
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import views, permissions, status
from rest_framework.response import Response

from apps.autenticacion.models import Usuario
from apps.utils.permissions import IsAdminOrFuncionario
from apps.solicitudes.models import Solicitud
from apps.funcionarios.models import Funcionario


def _solicitudes_para_usuario(user: Usuario):
    """Devuelve el queryset base según rol. Admin ve todo, funcionario su dependencia."""
    if getattr(user, "rol", None) == "admin":
        return Solicitud.objects.all()
    if getattr(user, "funcionario", None):
        return Solicitud.objects.filter(
            categoria__dependencia_municipal=user.funcionario.dependencia
        )
    return Solicitud.objects.none()


class SolicitudAnaliticaView(views.APIView):
    """
    Estadísticas básicas de solicitudes para funcionarios
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user

        queryset = _solicitudes_para_usuario(user)

        data = queryset.aggregate(
            realizadas=Count("id"),
            aprobadas=Count("id", filter=Q(estado="completada")),
            rechazadas=Count("id", filter=Q(estado="rechazada")),
        )

        return Response(data)


class EstadisticasCompletasView(views.APIView):
    """
    Estadísticas completas de solicitudes para funcionarios
    Incluye tiempos de respuesta, por dependencia, funcionario, localidad
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user

        # Filtros opcionales
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")
        estado = request.query_params.get("estado")
        categoria_id = request.query_params.get("categoria")

        queryset = _solicitudes_para_usuario(user)

        # Aplicar filtros
        if fecha_inicio:
            queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
        if estado:
            queryset = queryset.filter(estado=estado)
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        # Calcular tiempo promedio de respuesta (de creación a actualización)
        solicitudes_con_tiempo = queryset.exclude(
            fecha_actualizacion=F("fecha_creacion")
        ).annotate(
            tiempo_respuesta=ExpressionWrapper(
                F("fecha_actualizacion") - F("fecha_creacion"),
                output_field=DurationField(),
            )
        )

        tiempo_promedio = solicitudes_con_tiempo.aggregate(
            promedio=Avg("tiempo_respuesta")
        )

        # Convertir tiempo promedio a horas
        tiempo_promedio_horas = None
        if tiempo_promedio["promedio"]:
            tiempo_promedio_horas = tiempo_promedio["promedio"].total_seconds() / 3600

        # Solicitudes por estado
        por_estado = (
            queryset.values("estado").annotate(total=Count("id")).order_by("-total")
        )

        # Solicitudes por categoría
        por_categoria = (
            queryset.values("categoria__nombre", "categoria_id")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )

        # Solicitudes por localidad (si el ciudadano tiene localidad)
        por_localidad = (
            queryset.exclude(ciudadano__localidad__isnull=True)
            .values("ciudadano__localidad__colonia", "ciudadano__localidad_id")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )

        # Tendencia mensual
        tendencia_mensual = (
            queryset.annotate(mes=TruncMonth("fecha_creacion"))
            .values("mes")
            .annotate(total=Count("id"))
            .order_by("mes")
        )

        data = {
            "resumen": {
                "total_solicitudes": queryset.count(),
                "completadas": queryset.filter(estado="completada").count(),
                "rechazadas": queryset.filter(estado="rechazada").count(),
                "enviadas": queryset.filter(estado="enviada").count(),
                "vistas": queryset.filter(estado="visto").count(),
                "tiempo_promedio_respuesta_horas": (
                    round(tiempo_promedio_horas, 2) if tiempo_promedio_horas else None
                ),
            },
            "por_estado": list(por_estado),
            "por_categoria": list(por_categoria),
            "por_localidad": list(por_localidad),
            "tendencia_mensual": list(tendencia_mensual),
        }

        # Si es admin, agregar analíticas avanzadas
        if getattr(user, "rol", None) == "admin":
            from apps.dependecias_municipales.models import DependenciaMunicipal
            from apps.ciudadanos.models import Ciudadano
            from apps.solicitudes.models import Comentario

            # Rendimiento de funcionarios
            rendimiento_funcionarios = []
            for funcionario in Funcionario.objects.select_related(
                "dependencia", "usuario"
            ):
                solicitudes_dependencia = queryset.filter(
                    categoria__dependencia_municipal=funcionario.dependencia
                )

                total_asignadas = solicitudes_dependencia.count()
                if total_asignadas == 0:
                    continue

                comentarios_funcionario = Comentario.objects.filter(
                    solicitud__in=solicitudes_dependencia,
                    creado_por=(
                        str(funcionario.usuario)
                        if funcionario.usuario
                        else funcionario.nombre_completo
                    ),
                ).count()

                completadas = solicitudes_dependencia.filter(
                    estado="completada"
                ).count()
                tasa_resolucion = (
                    round((completadas / total_asignadas * 100), 2)
                    if total_asignadas > 0
                    else 0
                )

                rendimiento_funcionarios.append(
                    {
                        "id": funcionario.id,
                        "nombre": funcionario.nombre_completo,
                        "cargo": funcionario.cargo,
                        "dependencia": funcionario.dependencia.nombre,
                        "solicitudes_asignadas": total_asignadas,
                        "comentarios_realizados": comentarios_funcionario,
                        "solicitudes_completadas": completadas,
                        "tasa_resolucion": tasa_resolucion,
                    }
                )

            rendimiento_funcionarios.sort(
                key=lambda x: x["tasa_resolucion"], reverse=True
            )

            # Solicitudes por localidad detallada (Top 20)
            solicitudes_por_localidad_detallada = list(
                queryset.exclude(ciudadano__localidad__isnull=True)
                .values(
                    localidad=F("ciudadano__localidad__colonia"),
                    codigo_postal=F("ciudadano__localidad__codigo_postal"),
                    municipio=F("ciudadano__localidad__municipio"),
                )
                .annotate(total_solicitudes=Count("id"))
                .order_by("-total_solicitudes")[:20]
            )

            # Solicitudes por dependencia
            solicitudes_por_dependencia = list(
                queryset.values(
                    dependencia_id=F("categoria__dependencia_municipal__id"),
                    dependencia=F("categoria__dependencia_municipal__nombre"),
                )
                .annotate(
                    total=Count("id"),
                    completadas=Count("id", filter=Q(estado="completada")),
                    en_proceso=Count("id", filter=Q(estado__in=["enviada", "visto"])),
                    rechazadas=Count("id", filter=Q(estado="rechazada")),
                )
                .order_by("-total")
            )

            # Tiempo de resolución por dependencia
            tiempo_resolucion_dependencia = []
            for dep in DependenciaMunicipal.objects.all():
                solicitudes_completadas = queryset.filter(
                    categoria__dependencia_municipal=dep, estado="completada"
                )

                if solicitudes_completadas.exists():
                    tiempos = []
                    for sol in solicitudes_completadas:
                        tiempo = (
                            sol.fecha_actualizacion - sol.fecha_creacion
                        ).total_seconds() / 3600
                        tiempos.append(tiempo)

                    promedio = round(sum(tiempos) / len(tiempos), 2) if tiempos else 0

                    tiempo_resolucion_dependencia.append(
                        {
                            "dependencia": dep.nombre,
                            "tiempo_promedio_horas": promedio,
                            "solicitudes_completadas": len(tiempos),
                        }
                    )

            tiempo_resolucion_dependencia.sort(key=lambda x: x["tiempo_promedio_horas"])

            # Ciudadanos activos y por sexo
            ciudadanos_activos = (
                Ciudadano.objects.filter(
                    solicitudes__fecha_creacion__gte=timezone.now() - timedelta(days=30)
                )
                .distinct()
                .count()
            )

            ciudadanos_por_sexo = list(
                Ciudadano.objects.values("sexo").annotate(total=Count("id"))
            )

            data["admin_avanzado"] = {
                "rendimiento_funcionarios": rendimiento_funcionarios,
                "solicitudes_por_localidad_detallada": solicitudes_por_localidad_detallada,
                "solicitudes_por_dependencia": solicitudes_por_dependencia,
                "tiempo_resolucion_por_dependencia": tiempo_resolucion_dependencia,
                "ciudadanos_activos_ultimo_mes": ciudadanos_activos,
                "ciudadanos_por_sexo": ciudadanos_por_sexo,
                "total_ciudadanos": Ciudadano.objects.count(),
                "total_funcionarios": Funcionario.objects.count(),
            }

        return Response(data)


class SolicitudesPorPeriodoView(views.APIView):
    """
    Solicitudes agrupadas por periodo (día, semana, mes)
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user
        periodo = request.query_params.get("periodo", "dia")  # dia, semana, mes

        queryset = _solicitudes_para_usuario(user)

        # Agrupar según periodo
        if periodo == "dia":
            agrupado = (
                queryset.annotate(fecha=TruncDate("fecha_creacion"))
                .values("fecha")
                .annotate(
                    total=Count("id"),
                    completadas=Count("id", filter=Q(estado="completada")),
                    rechazadas=Count("id", filter=Q(estado="rechazada")),
                    enviadas=Count("id", filter=Q(estado="enviada")),
                    vistas=Count("id", filter=Q(estado="visto")),
                )
                .order_by("-fecha")[:30]
            )
        elif periodo == "semana":
            agrupado = (
                queryset.annotate(fecha=TruncWeek("fecha_creacion"))
                .values("fecha")
                .annotate(
                    total=Count("id"),
                    completadas=Count("id", filter=Q(estado="completada")),
                    rechazadas=Count("id", filter=Q(estado="rechazada")),
                    enviadas=Count("id", filter=Q(estado="enviada")),
                    vistas=Count("id", filter=Q(estado="visto")),
                )
                .order_by("-fecha")[:12]
            )
        else:  # mes
            agrupado = (
                queryset.annotate(fecha=TruncMonth("fecha_creacion"))
                .values("fecha")
                .annotate(
                    total=Count("id"),
                    completadas=Count("id", filter=Q(estado="completada")),
                    rechazadas=Count("id", filter=Q(estado="rechazada")),
                    enviadas=Count("id", filter=Q(estado="enviada")),
                    vistas=Count("id", filter=Q(estado="visto")),
                )
                .order_by("-fecha")[:12]
            )

        return Response({"periodo": periodo, "datos": list(agrupado)})


class RankingFuncionariosView(views.APIView):
    """
    Ranking de funcionarios por desempeño
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user

        # Si es admin, mostrar todos los funcionarios; de lo contrario, solo su dependencia
        if getattr(user, "rol", None) == "admin":
            funcionarios = Funcionario.objects.all()
        else:
            funcionarios = Funcionario.objects.filter(
                dependencia=user.funcionario.dependencia
            )

        # Por ahora, ranking por número de solicitudes en su dependencia
        # En el futuro se puede mejorar con solicitudes atendidas directamente
        ranking_data = []

        for funcionario in funcionarios:
            solicitudes_dependencia = Solicitud.objects.filter(
                categoria__dependencia_municipal=funcionario.dependencia
            )

            total = solicitudes_dependencia.count()
            completadas = solicitudes_dependencia.filter(estado="completada").count()

            tasa_completadas = (completadas / total * 100) if total > 0 else 0

            ranking_data.append(
                {
                    "id": funcionario.id,
                    "nombre": funcionario.nombre_completo,
                    "cargo": funcionario.cargo,
                    "dependencia": funcionario.dependencia.nombre,
                    "total_solicitudes": total,
                    "completadas": completadas,
                    "tasa_completadas": round(tasa_completadas, 2),
                }
            )

        # Ordenar por tasa de completadas
        ranking_data.sort(key=lambda x: x["tasa_completadas"], reverse=True)

        return Response({"ranking": ranking_data})


class MapaCalorGeograficoView(views.APIView):
    """
    Mapa de calor geográfico de solicitudes por localidad
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user

        queryset = _solicitudes_para_usuario(user).exclude(
            ciudadano__localidad__isnull=True
        )

        # Agrupar por localidad
        mapa_data = (
            queryset.values("ciudadano__localidad__colonia", "ciudadano__localidad_id")
            .annotate(
                total=Count("id"),
                completadas=Count("id", filter=Q(estado="completada")),
                rechazadas=Count("id", filter=Q(estado="rechazada")),
                pendientes=Count("id", filter=Q(estado__in=["enviada", "visto"])),
            )
            .order_by("-total")
        )

        return Response({"localidades": list(mapa_data)})


class AlertasSolicitudesView(views.APIView):
    """
    Alertas de solicitudes críticas o con mayor demora
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user

        queryset = _solicitudes_para_usuario(user)

        # Solicitudes antiguas sin atender (más de 7 días)
        fecha_limite = timezone.now() - timedelta(days=7)
        solicitudes_antiguas = queryset.filter(
            estado__in=["enviada", "visto"], fecha_creacion__lte=fecha_limite
        ).order_by("fecha_creacion")[:10]

        # Solicitudes recientes (últimas 24 horas)
        fecha_reciente = timezone.now() - timedelta(hours=24)
        solicitudes_recientes = queryset.filter(
            fecha_creacion__gte=fecha_reciente
        ).order_by("-fecha_creacion")[:10]

        # Serializar datos básicos
        antiguas_data = [
            {
                "id": s.id,
                "folio": s.folio,
                "categoria": s.categoria.nombre,
                "estado": s.estado,
                "fecha_creacion": s.fecha_creacion,
                "dias_antiguedad": (timezone.now() - s.fecha_creacion).days,
                "ciudadano": s.ciudadano.nombre_completo,
            }
            for s in solicitudes_antiguas
        ]

        recientes_data = [
            {
                "id": s.id,
                "folio": s.folio,
                "categoria": s.categoria.nombre,
                "estado": s.estado,
                "fecha_creacion": s.fecha_creacion,
                "ciudadano": s.ciudadano.nombre_completo,
            }
            for s in solicitudes_recientes
        ]

        return Response(
            {
                "solicitudes_antiguas": antiguas_data,
                "solicitudes_recientes": recientes_data,
                "total_pendientes": queryset.filter(
                    estado__in=["enviada", "visto"]
                ).count(),
            }
        )


class ComparacionPeriodosView(views.APIView):
    """
    Comparación de solicitudes entre dos periodos
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user

        # Obtener fechas de los periodos
        periodo1_inicio = request.query_params.get("periodo1_inicio")
        periodo1_fin = request.query_params.get("periodo1_fin")
        periodo2_inicio = request.query_params.get("periodo2_inicio")
        periodo2_fin = request.query_params.get("periodo2_fin")

        if not all([periodo1_inicio, periodo1_fin, periodo2_inicio, periodo2_fin]):
            # Por defecto: comparar este mes vs mes anterior
            hoy = timezone.now()
            periodo2_fin = hoy
            periodo2_inicio = hoy.replace(day=1)

            # Mes anterior
            if periodo2_inicio.month == 1:
                periodo1_fin = periodo2_inicio.replace(
                    year=periodo2_inicio.year - 1, month=12
                )
            else:
                periodo1_fin = periodo2_inicio.replace(month=periodo2_inicio.month - 1)

            periodo1_inicio = periodo1_fin.replace(day=1)

        queryset = _solicitudes_para_usuario(user)

        # Estadísticas periodo 1
        periodo1_queryset = queryset.filter(
            fecha_creacion__gte=periodo1_inicio, fecha_creacion__lte=periodo1_fin
        )

        stats_periodo1 = periodo1_queryset.aggregate(
            total=Count("id"),
            completadas=Count("id", filter=Q(estado="completada")),
            rechazadas=Count("id", filter=Q(estado="rechazada")),
            enviadas=Count("id", filter=Q(estado="enviada")),
            vistas=Count("id", filter=Q(estado="visto")),
        )

        # Estadísticas periodo 2
        periodo2_queryset = queryset.filter(
            fecha_creacion__gte=periodo2_inicio, fecha_creacion__lte=periodo2_fin
        )

        stats_periodo2 = periodo2_queryset.aggregate(
            total=Count("id"),
            completadas=Count("id", filter=Q(estado="completada")),
            rechazadas=Count("id", filter=Q(estado="rechazada")),
            enviadas=Count("id", filter=Q(estado="enviada")),
            vistas=Count("id", filter=Q(estado="visto")),
        )

        # Calcular diferencias
        diferencia = {}
        for key in stats_periodo1.keys():
            valor1 = stats_periodo1[key] or 0
            valor2 = stats_periodo2[key] or 0
            diferencia[key] = valor2 - valor1
            if valor1 > 0:
                diferencia[f"{key}_porcentaje"] = round(
                    (valor2 - valor1) / valor1 * 100, 2
                )
            else:
                diferencia[f"{key}_porcentaje"] = 0

        return Response(
            {
                "periodo1": {
                    "inicio": periodo1_inicio,
                    "fin": periodo1_fin,
                    "estadisticas": stats_periodo1,
                },
                "periodo2": {
                    "inicio": periodo2_inicio,
                    "fin": periodo2_fin,
                    "estadisticas": stats_periodo2,
                },
                "diferencia": diferencia,
            }
        )


class ReportePDFView(views.APIView):
    """
    Reporte PDF con resumen de solicitudes (solo admin)
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def _build_pdf_bytes(
        self, total: int, completadas: int, rechazadas: int, pendientes: int
    ) -> bytes:
        """Genera un PDF minimalista sin dependencias externas."""
        resumen = [
            ("Total", total),
            ("Completadas", completadas),
            ("Rechazadas", rechazadas),
            ("Pendientes", pendientes),
        ]

        stream_lines = [
            "BT /F1 14 Tf 72 740 Td (Reporte Analitica de Solicitudes) Tj ET",
        ]

        y = 710
        for label, valor in resumen:
            stream_lines.append(f"BT /F1 12 Tf 72 {y} Td ({label}: {valor}) Tj ET")
            y -= 20

        stream_bytes = "\n".join(stream_lines).encode("latin-1", errors="replace")

        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 6 0 R >> >> /Contents 4 0 R >>",
            b"<< /Length %d >>\nstream\n" % len(stream_bytes)
            + stream_bytes
            + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        ]

        buffer = bytearray()
        buffer.extend(b"%PDF-1.4\n")
        offsets = []

        for index, obj in enumerate(objects, start=1):
            offsets.append(len(buffer))
            buffer.extend(f"{index} 0 obj\n".encode("ascii"))
            buffer.extend(obj)
            buffer.extend(b"\nendobj\n")

        startxref = len(buffer)
        size = len(objects) + 1

        buffer.extend(b"xref\n")
        buffer.extend(f"0 {size}\n".encode("ascii"))
        buffer.extend(b"0000000000 65535 f \n")
        for offset in offsets:
            buffer.extend(f"{offset:010} 00000 n \n".encode("ascii"))

        buffer.extend(f"trailer << /Size {size} /Root 1 0 R >>\n".encode("ascii"))
        buffer.extend(b"startxref\n")
        buffer.extend(f"{startxref}\n".encode("ascii"))
        buffer.extend(b"%%EOF\n")

        return bytes(buffer)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user
        if getattr(user, "rol", None) != "admin":
            return Response(
                {"detail": "Solo administradores"}, status=status.HTTP_403_FORBIDDEN
            )

        queryset = Solicitud.objects.filter(
            categoria__dependencia_municipal=user.funcionario.dependencia
        )

        total = queryset.count()
        completadas = queryset.filter(estado="completada").count()
        rechazadas = queryset.filter(estado="rechazada").count()
        pendientes = queryset.filter(estado__in=["enviada", "visto"]).count()

        pdf_bytes = self._build_pdf_bytes(total, completadas, rechazadas, pendientes)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_analitica.pdf"'
        return response


class ExportarSolicitudesView(views.APIView):
    """
    Exportar solicitudes a CSV
    """

    permission_classes = (permissions.IsAuthenticated, IsAdminOrFuncionario)

    def get(self, request: views.Request, *args, **kwargs):
        user: Usuario = request.user

        # Filtros opcionales
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")
        estado = request.query_params.get("estado")
        categoria_id = request.query_params.get("categoria")

        queryset = _solicitudes_para_usuario(user).select_related(
            "categoria", "ciudadano", "ciudadano__localidad"
        )

        # Aplicar filtros
        if fecha_inicio:
            queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
        if estado:
            queryset = queryset.filter(estado=estado)
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        # Crear respuesta CSV
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="solicitudes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )

        # Agregar BOM para Excel
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow(
            [
                "Folio",
                "Categoría",
                "Estado",
                "Ciudadano",
                "Localidad",
                "Descripción",
                "Fecha Creación",
                "Fecha Actualización",
                "Días Transcurridos",
            ]
        )

        for solicitud in queryset:
            dias_transcurridos = (timezone.now() - solicitud.fecha_creacion).days
            localidad = (
                solicitud.ciudadano.localidad.colonia
                if solicitud.ciudadano.localidad
                else "N/A"
            )

            writer.writerow(
                [
                    solicitud.folio,
                    solicitud.categoria.nombre,
                    solicitud.get_estado_display(),
                    solicitud.ciudadano.nombre_completo,
                    localidad,
                    solicitud.descripcion[:100],  # Limitar a 100 caracteres
                    solicitud.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                    solicitud.fecha_actualizacion.strftime("%Y-%m-%d %H:%M:%S"),
                    dias_transcurridos,
                ]
            )

        return response
