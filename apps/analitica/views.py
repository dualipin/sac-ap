from django.db.models import Count, Avg, Q, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.solicitudes.models import Solicitud, Comentario
from apps.funcionarios.models import Funcionario
from apps.ciudadanos.models import Ciudadano
from apps.dependecias_municipales.models import DependenciaMunicipal
from apps.utils.permissions import IsAdmin


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def analiticas_administrador(request):
    """
    Dashboard completo de analíticas para administradores.
    Incluye: métricas generales, rendimiento de funcionarios, solicitudes por localidad,
    tendencias temporales, etc.
    """
    # Parámetros de fecha opcionales
    fecha_inicio_str = request.query_params.get("fecha_inicio")
    fecha_fin_str = request.query_params.get("fecha_fin")

    # Filtros de fecha
    filtros_fecha = {}
    if fecha_inicio_str:
        try:
            fecha_inicio = timezone.datetime.fromisoformat(
                fecha_inicio_str.replace("Z", "+00:00")
            )
            filtros_fecha["fecha_creacion__gte"] = fecha_inicio
        except:
            pass

    if fecha_fin_str:
        try:
            fecha_fin = timezone.datetime.fromisoformat(
                fecha_fin_str.replace("Z", "+00:00")
            )
            filtros_fecha["fecha_creacion__lte"] = fecha_fin
        except:
            pass

    # Si no hay filtros, usar últimos 30 días
    if not filtros_fecha:
        hace_30_dias = timezone.now() - timedelta(days=30)
        filtros_fecha["fecha_creacion__gte"] = hace_30_dias

    # 1. MÉTRICAS GENERALES
    total_solicitudes = Solicitud.objects.filter(**filtros_fecha).count()
    total_ciudadanos = Ciudadano.objects.count()
    total_funcionarios = Funcionario.objects.count()

    solicitudes_por_estado = list(
        Solicitud.objects.filter(**filtros_fecha)
        .values("estado")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # 2. RENDIMIENTO DE FUNCIONARIOS
    # Calcular solicitudes atendidas por funcionario (basado en comentarios)
    rendimiento_funcionarios = []

    for funcionario in Funcionario.objects.select_related("dependencia", "usuario"):
        # Solicitudes de su dependencia
        solicitudes_dependencia = Solicitud.objects.filter(
            categoria__dependencia_municipal=funcionario.dependencia, **filtros_fecha
        )

        total_asignadas = solicitudes_dependencia.count()

        # Comentarios creados por este funcionario
        comentarios_funcionario = Comentario.objects.filter(
            solicitud__categoria__dependencia_municipal=funcionario.dependencia,
            creado_por=(
                str(funcionario.usuario)
                if funcionario.usuario
                else funcionario.nombre_completo
            ),
            solicitud__in=solicitudes_dependencia,
        ).count()

        # Solicitudes completadas de su dependencia
        completadas = solicitudes_dependencia.filter(estado="completada").count()

        # Tiempo promedio de respuesta (primera interacción)
        solicitudes_con_comentario = (
            solicitudes_dependencia.filter(comentarios__isnull=False)
            .annotate(
                tiempo_primera_respuesta=ExpressionWrapper(
                    F("comentarios__fecha_creacion") - F("fecha_creacion"),
                    output_field=DurationField(),
                )
            )
            .values_list("tiempo_primera_respuesta", flat=True)
        )

        tiempo_promedio_respuesta = None
        if solicitudes_con_comentario:
            tiempos = [
                t.total_seconds() / 3600 for t in solicitudes_con_comentario if t
            ]  # en horas
            if tiempos:
                tiempo_promedio_respuesta = round(sum(tiempos) / len(tiempos), 2)

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
                "tiempo_promedio_respuesta_horas": tiempo_promedio_respuesta,
            }
        )

    # Ordenar por tasa de resolución
    rendimiento_funcionarios.sort(key=lambda x: x["tasa_resolucion"], reverse=True)

    # 3. SOLICITUDES POR LOCALIDAD
    solicitudes_por_localidad = list(
        Solicitud.objects.filter(**filtros_fecha)
        .select_related("ciudadano__localidad")
        .values(
            localidad=F("ciudadano__localidad__colonia"),
            codigo_postal=F("ciudadano__localidad__codigo_postal"),
            municipio=F("ciudadano__localidad__municipio"),
        )
        .annotate(total_solicitudes=Count("id"))
        .order_by("-total_solicitudes")[:20]  # Top 20
    )

    # 4. SOLICITUDES POR DEPENDENCIA
    solicitudes_por_dependencia = list(
        Solicitud.objects.filter(**filtros_fecha)
        .select_related("categoria__dependencia_municipal")
        .values(
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

    # 5. TENDENCIAS TEMPORALES (últimos 30 días)
    tendencia_diaria = list(
        Solicitud.objects.filter(**filtros_fecha)
        .annotate(fecha=TruncDate("fecha_creacion"))
        .values("fecha")
        .annotate(total=Count("id"))
        .order_by("fecha")
    )

    # 6. CATEGORÍAS MÁS SOLICITADAS
    categorias_populares = list(
        Solicitud.objects.filter(**filtros_fecha)
        .values(categoria_id=F("categoria__id"), categoria=F("categoria__nombre"))
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # 7. TIEMPO PROMEDIO DE RESOLUCIÓN POR DEPENDENCIA
    tiempo_resolucion_dependencia = []
    for dep in DependenciaMunicipal.objects.all():
        solicitudes_completadas = Solicitud.objects.filter(
            categoria__dependencia_municipal=dep, estado="completada", **filtros_fecha
        )

        if solicitudes_completadas.exists():
            tiempos = []
            for sol in solicitudes_completadas:
                tiempo = (
                    sol.fecha_actualizacion - sol.fecha_creacion
                ).total_seconds() / 3600  # horas
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

    # 8. ESTADÍSTICAS DE CIUDADANOS
    ciudadanos_por_sexo = list(
        Ciudadano.objects.values("sexo").annotate(total=Count("id"))
    )

    ciudadanos_activos = (
        Ciudadano.objects.filter(
            solicitudes__fecha_creacion__gte=timezone.now() - timedelta(days=30)
        )
        .distinct()
        .count()
    )

    return Response(
        {
            "metricas_generales": {
                "total_solicitudes": total_solicitudes,
                "total_ciudadanos": total_ciudadanos,
                "total_funcionarios": total_funcionarios,
                "ciudadanos_activos_ultimo_mes": ciudadanos_activos,
                "solicitudes_por_estado": solicitudes_por_estado,
            },
            "rendimiento_funcionarios": rendimiento_funcionarios,
            "solicitudes_por_localidad": solicitudes_por_localidad,
            "solicitudes_por_dependencia": solicitudes_por_dependencia,
            "tendencia_diaria": tendencia_diaria,
            "categorias_populares": categorias_populares,
            "tiempo_resolucion_por_dependencia": tiempo_resolucion_dependencia,
            "ciudadanos_por_sexo": ciudadanos_por_sexo,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def rendimiento_funcionario_detalle(request, funcionario_id):
    """
    Detalle del rendimiento de un funcionario específico.
    """
    try:
        funcionario = Funcionario.objects.select_related("dependencia", "usuario").get(
            id=funcionario_id
        )
    except Funcionario.DoesNotExist:
        return Response(
            {"detail": "Funcionario no encontrado"}, status=status.HTTP_404_NOT_FOUND
        )

    # Parámetros de fecha
    fecha_inicio_str = request.query_params.get("fecha_inicio")
    fecha_fin_str = request.query_params.get("fecha_fin")

    filtros_fecha = {}
    if fecha_inicio_str:
        try:
            filtros_fecha["fecha_creacion__gte"] = timezone.datetime.fromisoformat(
                fecha_inicio_str.replace("Z", "+00:00")
            )
        except:
            pass
    if fecha_fin_str:
        try:
            filtros_fecha["fecha_creacion__lte"] = timezone.datetime.fromisoformat(
                fecha_fin_str.replace("Z", "+00:00")
            )
        except:
            pass

    if not filtros_fecha:
        hace_30_dias = timezone.now() - timedelta(days=30)
        filtros_fecha["fecha_creacion__gte"] = hace_30_dias

    # Solicitudes de su dependencia
    solicitudes = Solicitud.objects.filter(
        categoria__dependencia_municipal=funcionario.dependencia, **filtros_fecha
    )

    total_solicitudes = solicitudes.count()
    completadas = solicitudes.filter(estado="completada").count()
    en_proceso = solicitudes.filter(estado__in=["enviada", "visto"]).count()
    rechazadas = solicitudes.filter(estado="rechazada").count()

    # Comentarios del funcionario
    usuario_str = (
        str(funcionario.usuario) if funcionario.usuario else funcionario.nombre_completo
    )
    comentarios = Comentario.objects.filter(
        creado_por=usuario_str, solicitud__in=solicitudes
    )

    total_comentarios = comentarios.count()

    # Actividad por día
    actividad_diaria = list(
        comentarios.annotate(fecha=TruncDate("fecha_creacion"))
        .values("fecha")
        .annotate(comentarios=Count("id"))
        .order_by("fecha")
    )

    # Solicitudes atendidas por categoría
    por_categoria = list(
        solicitudes.values(categoria=F("categoria__nombre"))
        .annotate(
            total=Count("id"), completadas=Count("id", filter=Q(estado="completada"))
        )
        .order_by("-total")
    )

    return Response(
        {
            "funcionario": {
                "id": funcionario.id,
                "nombre": funcionario.nombre_completo,
                "cargo": funcionario.cargo,
                "dependencia": funcionario.dependencia.nombre,
            },
            "resumen": {
                "total_solicitudes": total_solicitudes,
                "completadas": completadas,
                "en_proceso": en_proceso,
                "rechazadas": rechazadas,
                "tasa_resolucion": (
                    round((completadas / total_solicitudes * 100), 2)
                    if total_solicitudes > 0
                    else 0
                ),
                "total_comentarios": total_comentarios,
            },
            "actividad_diaria": actividad_diaria,
            "por_categoria": por_categoria,
        },
        status=status.HTTP_200_OK,
    )
