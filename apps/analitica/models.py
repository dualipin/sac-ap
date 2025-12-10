import hashlib
from django.db import models
from django.utils import timezone


class UserAgent(models.Model):
    """
    UserAgent (deduplicado por hash)
    """
    hash = models.CharField(max_length=64, unique=True, db_index=True)
    text = models.TextField()

    class Meta:
        db_table = "analytics_user_agents"

    @classmethod
    def get_or_create_from_string(cls, ua_string: str):
        if not ua_string:
            return None
        ua_hash = hashlib.sha256(ua_string.encode("utf-8")).hexdigest()
        ua, created = cls.objects.get_or_create(hash=ua_hash, defaults={"text": ua_string})
        return ua

    def __str__(self):
        return (self.text or "")[:120]


class Visitante(models.Model):
    """
    Visitante
    """
    visitante_id = models.CharField(max_length=255, db_index=True, db_column="vid")
    primera_visita = models.DateTimeField(auto_now_add=True, db_column="pv", db_index=True)
    ultima_visita = models.DateTimeField(auto_now=True, db_column="up")
    user_agent = models.ForeignKey(UserAgent, null=True, blank=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(blank=True, null=True, db_column="ip")
    tipo_dispositivo = models.CharField(max_length=50, blank=True)
    pais = models.CharField(max_length=100, blank=True, db_index=True)
    ciudad = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "analytics_visitantes"
        indexes = [
            models.Index(fields=["visitante_id"]),
            models.Index(fields=["pais"]),
            models.Index(fields=["primera_visita"]),
        ]

    def __str__(self):
        return f"{self.visitante_id} {self.ip}"


class Sesion(models.Model):
    """
    Administra las sesiones de los usuarios y visitantes
    """
    sesion_id = models.CharField(max_length=255, unique=True, db_index=True, db_column="sid")
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name="sesiones", db_column="vid")
    inicio = models.DateTimeField(db_index=True, db_column="ini")
    fin = models.DateTimeField(null=True, blank=True)
    # la duracion se calcula/almacena para analítica rápida
    duracion_segundos = models.IntegerField(null=True, blank=True, db_column="dur")
    conteo_paginas = models.IntegerField(default=0, db_column="cnp", db_index=True)
    es_rebote = models.BooleanField(default=False, db_column="reb", db_index=True)
    ultima_actividad = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "analytics_sesiones"
        indexes = [
            models.Index(fields=["inicio"]),
            models.Index(fields=["fin"]),
            models.Index(fields=["visitante", "inicio"]),
        ]

    def __str__(self):
        return f"Sesion {self.sesion_id} (vid={self.visitante.visitante_id})"

    @property
    def duracion(self):
        if self.fin and self.inicio:
            return (self.fin - self.inicio).total_seconds()
        return None

    def terminar(self, cierre_time=None):
        """
        Cierra la sesión: calcula duración, actualiza conteos y marca rebote si corresponde.
        Debe llamarse desde un endpoint `session_end` o tarea que detecte inactividad.
        """
        cierre_time = cierre_time or timezone.now()
        self.fin = cierre_time
        # si no se almacenó duracion explícita, calcular de inicio->fin
        if self.inicio:
            dur = (self.fin - self.inicio).total_seconds()
            self.duracion_segundos = int(dur)
        # rebote: si conteo de páginas <= 1
        self.es_rebote = self.conteo_paginas <= 1
        self.save(update_fields=["fin", "duracion_segundos", "es_rebote"])


class PaginaVista(models.Model):
    """
    Visitas de cada pagina
    """
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="paginas_vistas")
    ruta = models.CharField(max_length=2000, db_index=True)
    nombre_pagina = models.CharField(max_length=500, blank=True)
    hora = models.DateTimeField(db_index=True)
    tiempo_en_pagina = models.IntegerField(null=True, blank=True)
    referencia = models.URLField(blank=True)
    utm_data = models.JSONField(default=dict, blank=True)
    user_agent = models.ForeignKey(UserAgent, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "analytics_pagina_vista"
        indexes = [
            models.Index(fields=["hora"]),
            models.Index(fields=["ruta"]),
            models.Index(fields=["sesion"]),
        ]

    def __str__(self):
        return f"{self.ruta} @ {self.hora.isoformat()}"


class Evento(models.Model):
    """
    Logica de eventos para analítica
    """
    EVENT_TYPES = [
        ("page_view", "Pagina Vista"),
        ("custom_event", "Evento"),
        ("conversion", "Conversion"),
        ("error", "Error"),
    ]

    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="eventos", null=True, blank=True)
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    nombre = models.CharField(max_length=255)
    ruta = models.CharField(max_length=2000, db_index=True, blank=True)
    hora = models.DateTimeField(db_index=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "analytics_eventos"
        indexes = [
            models.Index(fields=["tipo", "hora"]),
            models.Index(fields=["visitante", "hora"]),
        ]

    def __str__(self):
        return f"{self.tipo}:{self.nombre} @{self.hora.isoformat()}"
