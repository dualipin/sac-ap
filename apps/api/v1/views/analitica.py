from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
from django.http import HttpResponse

from apps.analitica.models import Sesion, PaginaVista
from apps.analitica.serializers import (
    SesionStartSerializer,
    SesionEndSerializer,
    PaginaVistaBatchSerializer,
    EventoBatchSerializer,
    PaginaVistaSerializer,
    EventoSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics


class PaginaVistaCreateView(APIView):
    def post(self, request):
        serializer = PaginaVistaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"ok": True}, status=status.HTTP_201_CREATED)


class EventoCreateView(APIView):
    def post(self, request):
        serializer = EventoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"ok": True}, status=status.HTTP_201_CREATED)


class SesionListView(generics.ListAPIView):
    queryset = Sesion.objects.all().select_related("visitante")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["inicio", "fin", "es_rebote", "visitante__pais"]


class SesionStartView(APIView):
    """
    POST body:
    { "visitante_id": "v1", "sesion_id": "s1", "user_agent": "...", "inicio": "ISO" }
    """

    def post(self, request):
        serializer = SesionStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.create(serializer.validated_data)
        sesion = data["sesion"]
        return Response(
            {"sesion_id": sesion.sesion_id, "created": data["created"]},
            status=status.HTTP_201_CREATED,
        )


class SesionEndView(APIView):
    """
    POST body:
    { "visitante_id": "v1", "sesion_id": "s1", "fin": "ISO" }
    """

    def post(self, request):
        serializer = SesionEndSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sesion = serializer.save()
        return Response(
            {
                "sesion_id": sesion.sesion_id,
                "duracion": sesion.duracion,
                "es_rebote": sesion.es_rebote,
            }
        )


class PaginaVistaBatchView(APIView):
    """
    POST body:
    { "items": [ { visitante_id, sesion_id, ruta, hora, tiempo_en_pagina, ... }, ... ] }
    """

    def post(self, request):
        serializer = PaginaVistaBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = serializer.create(serializer.validated_data)
        return Response({"created": len(created)}, status=status.HTTP_201_CREATED)


class EventoBatchView(APIView):
    """
    POST body:
    { "items": [ { visitante_id, sesion_id(optional), tipo, nombre, hora, metadata }, ... ] }
    """

    def post(self, request):
        serializer = EventoBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = serializer.create(serializer.validated_data)
        return Response({"created": len(created)}, status=status.HTTP_201_CREATED)


from django.db.models import Count, Avg
from django.db.models.functions import TruncDate


class StatsSummaryView(APIView):
    permission_classes = [IsAuthenticated]  # require auth for stats

    def get(self, request):
        # optional filters: start, end, pais, device
        qp = request.query_params
        start = qp.get("start")
        end = qp.get("end")

        qs_s = Sesion.objects.all()
        qs_pv = PaginaVista.objects.all()
        if start:
            qs_s = qs_s.filter(inicio__gte=start)
            qs_pv = qs_pv.filter(hora__gte=start)
        if end:
            qs_s = qs_s.filter(inicio__lte=end)
            qs_pv = qs_pv.filter(hora__lte=end)

        total_sessions = qs_s.count()
        total_visitors = qs_s.values("visitante").distinct().count()
        total_pageviews = qs_pv.count()
        bounce_rate = qs_s.filter(es_rebote=True).count() / max(total_sessions, 1)
        avg_session = (
            qs_s.filter(duracion_segundos__isnull=False).aggregate(
                avg=Avg("duracion_segundos")
            )["avg"]
            or 0
        )
        avg_page = (
            qs_pv.filter(tiempo_en_pagina__isnull=False).aggregate(
                avg=Avg("tiempo_en_pagina")
            )["avg"]
            or 0
        )

        return Response(
            {
                "total_sessions": total_sessions,
                "total_visitors": total_visitors,
                "total_pageviews": total_pageviews,
                "bounce_rate": round(bounce_rate * 100, 2),
                "avg_session_seconds": round(avg_session, 2),
                "avg_page_seconds": round(avg_page, 2),
            }
        )


class DailyPageviewsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        start = timezone.now() - timedelta(days=days)
        qs = (
            PaginaVista.objects.filter(hora__gte=start)
            .annotate(date=TruncDate("hora"))
            .values("date")
            .annotate(views=Count("id"))
            .order_by("date")
        )
        return Response(list(qs))


class TopPagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        qs = (
            PaginaVista.objects.values("ruta")
            .annotate(views=Count("id"))
            .order_by("-views")[:limit]
        )
        return Response(list(qs))


class WebAnalyticsReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qp = request.query_params
        start = qp.get("start")
        end = qp.get("end")
        limit = int(qp.get("limit", 10))

        qs_s = Sesion.objects.all()
        qs_pv = PaginaVista.objects.all()
        if start:
            qs_s = qs_s.filter(inicio__gte=start)
            qs_pv = qs_pv.filter(hora__gte=start)
        if end:
            qs_s = qs_s.filter(inicio__lte=end)
            qs_pv = qs_pv.filter(hora__lte=end)

        total_sessions = qs_s.count()
        total_visitors = qs_s.values("visitante").distinct().count()
        total_pageviews = qs_pv.count()
        bounce_rate = qs_s.filter(es_rebote=True).count() / max(total_sessions, 1)
        avg_session = (
            qs_s.filter(duracion_segundos__isnull=False).aggregate(
                avg=Avg("duracion_segundos")
            )["avg"]
            or 0
        )
        avg_page = (
            qs_pv.filter(tiempo_en_pagina__isnull=False).aggregate(
                avg=Avg("tiempo_en_pagina")
            )["avg"]
            or 0
        )

        top_pages = list(
            qs_pv.values("ruta").annotate(views=Count("id")).order_by("-views")[:limit]
        )

        def _safe(text: str) -> str:
            cleaned = (text or "").replace("\\", "/")
            return cleaned.replace("(", "[").replace(")", "]")

        def _pdf_bytes():
            y_cursor = 780
            lines = []
            lines.append(f"BT /F1 18 Tf 50 {y_cursor} Td (Reporte Analitica Web) Tj ET")
            y_cursor -= 20
            if start or end:
                rango_txt = f"Rango: {start or '-'} a {end or '-'}"
                lines.append(
                    f"BT /F1 10 Tf 50 {y_cursor} Td ({_safe(rango_txt)}) Tj ET"
                )
                y_cursor -= 18

            resumen_items = [
                ("Sesiones", total_sessions),
                ("Visitantes unicos", total_visitors),
                ("Pageviews", total_pageviews),
                ("Bounce rate", f"{round(bounce_rate*100,2)}%"),
                ("Duracion media sesion (s)", round(avg_session, 2)),
                ("Tiempo medio pagina (s)", round(avg_page, 2)),
            ]
            for label, val in resumen_items:
                lines.append(
                    f"BT /F1 11 Tf 50 {y_cursor} Td ({_safe(label)}: {val}) Tj ET"
                )
                y_cursor -= 16

            lines.append(f"BT /F1 12 Tf 50 {y_cursor-8} Td (Top paginas) Tj ET")
            y_cursor -= 26
            lines.append(f"BT /F1 10 Tf 50 {y_cursor} Td (#) Tj ET")
            lines.append(f"BT /F1 10 Tf 70 {y_cursor} Td (Ruta) Tj ET")
            lines.append(f"BT /F1 10 Tf 450 {y_cursor} Td (Vistas) Tj ET")
            y_cursor -= 14

            idx = 1
            for page in top_pages:
                ruta = _safe(page["ruta"] or "sin-ruta")[:90]
                lines.append(f"BT /F1 10 Tf 50 {y_cursor} Td ({idx}) Tj ET")
                lines.append(f"BT /F1 10 Tf 70 {y_cursor} Td ({ruta}) Tj ET")
                lines.append(f"BT /F1 10 Tf 450 {y_cursor} Td ({page['views']}) Tj ET")
                y_cursor -= 12
                idx += 1

            stream_bytes = "\n".join(lines).encode("latin-1", errors="replace")

            # Build PDF objects
            objects = []
            # 1 Catalog
            objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
            # 2 Pages
            objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
            # 3 Page
            objects.append(
                b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
            )
            # 4 Contents
            objects.append(
                b"<< /Length %d >>\nstream\n" % len(stream_bytes)
                + stream_bytes
                + b"\nendstream"
            )
            # 5 Font
            objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

            buf = bytearray()
            buf.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
            offsets = []
            for i, obj in enumerate(objects, start=1):
                offsets.append(len(buf))
                buf.extend(f"{i} 0 obj\n".encode("ascii"))
                buf.extend(obj)
                buf.extend(b"\nendobj\n")

            startxref = len(buf)
            size = len(objects) + 1
            buf.extend(b"xref\n")
            buf.extend(f"0 {size}\n".encode("ascii"))
            buf.extend(b"0000000000 65535 f \n")
            for off in offsets:
                buf.extend(f"{off:010} 00000 n \n".encode("ascii"))
            buf.extend(f"trailer << /Size {size} /Root 1 0 R >>\n".encode("ascii"))
            buf.extend(b"startxref\n")
            buf.extend(f"{startxref}\n".encode("ascii"))
            buf.extend(b"%%EOF\n")
            return bytes(buf)

        pdf_bytes = _pdf_bytes()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="analitica_web.pdf"'
        return response
