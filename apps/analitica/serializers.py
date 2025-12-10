from rest_framework import serializers
from django.utils import timezone
from .models import UserAgent, Visitante, Sesion, PaginaVista, Evento


class IdPairSerializer(serializers.Serializer):
    visitante_id = serializers.CharField()
    sesion_id = serializers.CharField()


class UserAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAgent
        fields = ["id", "hash", "text"]


class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = [
            "id",
            "visitante_id",
            "primera_visita",
            "ultima_visita",
            "user_agent",
            "ip",
            "tipo_dispositivo",
            "pais",
            "ciudad",
        ]


class SesionStartSerializer(serializers.Serializer):
    visitante_id = serializers.CharField()
    sesion_id = serializers.CharField()
    user_agent = serializers.CharField(required=False, allow_blank=True)
    inicio = serializers.DateTimeField(required=False)

    def create(self, validated):
        ua_string = validated.get("user_agent", "")
        ua = UserAgent.get_or_create_from_string(ua_string) if ua_string else None

        visitante, _ = Visitante.objects.get_or_create(
            visitante_id=validated["visitante_id"],
            defaults={"user_agent": ua}
        )

        sesion, created = Sesion.objects.get_or_create(
            sesion_id=validated["sesion_id"],
            defaults={"visitante": visitante, "inicio": validated.get("inicio", timezone.now())}
        )
        # ensure visitante FK set if session existed without it
        if sesion.visitante_id != visitante.id:
            sesion.visitante = visitante
            sesion.save(update_fields=["visitante"])

        return {"sesion": sesion, "created": created}


class SesionEndSerializer(serializers.Serializer):
    visitante_id = serializers.CharField()
    sesion_id = serializers.CharField()
    fin = serializers.DateTimeField(required=False)

    def save(self):
        fin = self.validated_data.get("fin") or timezone.now()
        visitante_id = self.validated_data["visitante_id"]
        sesion_id = self.validated_data["sesion_id"]

        try:
            sesion = Sesion.objects.get(sesion_id=sesion_id, visitante__visitante_id=visitante_id)
        except Sesion.DoesNotExist:
            raise serializers.ValidationError("Sesion no encontrada.")

        sesion.fin = fin
        # duracion y rebote se calculan en terminar()
        sesion.terminar(cierre_time=fin)
        return sesion


class PaginaVistaItemSerializer(serializers.Serializer):
    visitante_id = serializers.CharField()
    sesion_id = serializers.CharField()
    ruta = serializers.CharField()
    nombre_pagina = serializers.CharField(required=False, allow_blank=True)
    hora = serializers.DateTimeField(required=False)
    tiempo_en_pagina = serializers.FloatField(required=False)
    referencia = serializers.CharField(required=False, allow_blank=True)
    utm_data = serializers.JSONField(required=False)
    user_agent = serializers.CharField(required=False, allow_blank=True)


class PaginaVistaBatchSerializer(serializers.Serializer):
    items = PaginaVistaItemSerializer(many=True)

    def create(self, validated):
        created = []
        now = timezone.now()
        for item in validated["items"]:
            ua = UserAgent.get_or_create_from_string(item.get("user_agent", "")) if item.get("user_agent") else None
            visitante, _ = Visitante.objects.get_or_create(visitante_id=item["visitante_id"],
                                                           defaults={"user_agent": ua})
            sesion, _ = Sesion.objects.get_or_create(sesion_id=item["sesion_id"],
                                                     defaults={"visitante": visitante, "inicio": item.get("hora", now)})
            # create pageview
            pv = PaginaVista.objects.create(
                sesion=sesion,
                ruta=item["ruta"],
                nombre_pagina=item.get("nombre_pagina", ""),
                hora=item.get("hora", now),
                tiempo_en_pagina=int(item["tiempo_en_pagina"]) if item.get("tiempo_en_pagina") else None,
                referencia=item.get("referencia", ""),
                utm_data=item.get("utm_data", {}),
                user_agent=ua
            )
            # update session counters atomically
            from django.db.models import F
            Sesion.objects.filter(pk=sesion.pk).update(conteo_paginas=F("conteo_paginas") + 1, ultima_actividad=now)
            created.append(pv)
        return created


class PaginaVistaSerializer(serializers.ModelSerializer):
    visitante_id = serializers.CharField(write_only=True)
    sesion_id = serializers.CharField(write_only=True)
    user_agent_string = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = PaginaVista
        fields = [
            "id",
            "visitante_id",
            "sesion_id",
            "ruta",
            "nombre_pagina",
            "hora",
            "tiempo_en_pagina",
            "referencia",
            "utm_data",
            "user_agent_string",
        ]

    def create(self, validated):
        ua = UserAgent.get_or_create_from_string(validated.get("user_agent_string", ""))

        try:
            sesion = Sesion.objects.get(
                sesion_id=validated["sesion_id"],
                visitante__visitante_id=validated["visitante_id"]
            )
        except Sesion.DoesNotExist:
            raise serializers.ValidationError("Sesión inválida.")

        sesion.conteo_paginas += 1
        sesion.save(update_fields=["conteo_paginas"])

        return PaginaVista.objects.create(
            sesion=sesion,
            ruta=validated["ruta"],
            nombre_pagina=validated.get("nombre_pagina", ""),
            hora=validated["hora"],
            tiempo_en_pagina=validated.get("tiempo_en_pagina"),
            referencia=validated.get("referencia", ""),
            utm_data=validated.get("utm_data", {}),
            user_agent=ua
        )


class EventoSerializer(serializers.ModelSerializer):
    visitante_id = serializers.CharField(write_only=True)
    sesion_id = serializers.CharField(write_only=True)

    class Meta:
        model = Evento
        fields = [
            "id",
            "visitante_id",
            "sesion_id",
            "tipo",
            "nombre",
            "ruta",
            "hora",
            "metadata",
        ]

    def create(self, validated):
        try:
            sesion = Sesion.objects.get(
                sesion_id=validated["sesion_id"],
                visitante__visitante_id=validated["visitante_id"]
            )
        except Sesion.DoesNotExist:
            raise serializers.ValidationError("Sesión inválida.")

        return Evento.objects.create(
            sesion=sesion,
            visitante=sesion.visitante,
            tipo=validated["tipo"],
            nombre=validated["nombre"],
            ruta=validated.get("ruta", ""),
            hora=validated["hora"],
            metadata=validated.get("metadata", {}),
        )


class EventoItemSerializer(serializers.Serializer):
    visitante_id = serializers.CharField()
    sesion_id = serializers.CharField(required=False, allow_blank=True)
    tipo = serializers.ChoiceField(choices=[c[0] for c in Evento.EVENT_TYPES])
    nombre = serializers.CharField()
    ruta = serializers.CharField(required=False, allow_blank=True)
    hora = serializers.DateTimeField(required=False)
    metadata = serializers.JSONField(required=False, default=dict)


class EventoBatchSerializer(serializers.Serializer):
    items = EventoItemSerializer(many=True)

    def create(self, validated):
        created = []
        now = timezone.now()
        for item in validated["items"]:
            visitante, _ = Visitante.objects.get_or_create(visitante_id=item["visitante_id"])
            sesion = None
            if item.get("sesion_id"):
                try:
                    sesion = Sesion.objects.get(sesion_id=item["sesion_id"], visitante=visitante)
                except Sesion.DoesNotExist:
                    sesion = None
            ev = Evento.objects.create(
                sesion=sesion,
                visitante=visitante,
                tipo=item["tipo"],
                nombre=item["nombre"],
                ruta=item.get("ruta", ""),
                hora=item.get("hora", now),
                metadata=item.get("metadata", {}),
            )
            created.append(ev)
        return created
