from rest_framework import serializers

from .models import Solicitud, Categoria, Comentario

MAX_ATTACHMENT_SIZE_MB = 5
MAX_ATTACHMENT_SIZE_BYTES = MAX_ATTACHMENT_SIZE_MB * 1024 * 1024


def validate_attachment_size(uploaded_file):
    """Valida el tamaño máximo permitido del archivo adjunto."""
    if uploaded_file and uploaded_file.size > MAX_ATTACHMENT_SIZE_BYTES:
        raise serializers.ValidationError(
            f"El archivo excede el límite de {MAX_ATTACHMENT_SIZE_MB}MB."
        )
    return uploaded_file


class CategoriasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "dependencia_municipal"]

    def validate_nombre(self, value):
        # Validar nombre duplicado
        qs = Categoria.objects.filter(nombre__iexact=value.strip())

        # Si es una actualización, excluir la instancia actual
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe una categoría con este nombre."
            )

        return value.strip()

    def validate(self, data):
        """Validación adicional para asegurar que el nombre sea único por dependencia"""
        nombre = data.get("nombre", self.instance.nombre if self.instance else None)
        dependencia = data.get(
            "dependencia_municipal",
            self.instance.dependencia_municipal if self.instance else None,
        )

        if nombre and dependencia:
            qs = Categoria.objects.filter(
                nombre__iexact=nombre.strip(),
                dependencia_municipal=dependencia,
            )

            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError(
                    {
                        "nombre": "Ya existe una categoría con este nombre en esta dependencia."
                    }
                )

        return data


class RegistrarSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields = ["categoria", "descripcion", "archivo_adjunto"]

    def validate(self, attrs):
        validate_attachment_size(attrs.get("archivo_adjunto"))
        return attrs

    def validate_descripcion(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "La descripción debe tener al menos 10 caracteres."
            )
        if len(value) > 2000:
            raise serializers.ValidationError(
                "La descripción no puede exceder 2000 caracteres."
            )
        return value


class ComentarioSerializer(serializers.ModelSerializer):
    archivo_adjunto = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = ["id", "texto", "archivo_adjunto", "fecha_creacion", "creado_por"]

    def get_archivo_adjunto(self, obj):
        """Retorna la URL completa del archivo si existe"""
        if obj.archivo_adjunto:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.archivo_adjunto.url)
            return obj.archivo_adjunto.url
        return None


class SolicitudSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    folio = serializers.CharField(read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    archivo_adjunto = serializers.SerializerMethodField()

    class Meta:
        model = Solicitud
        fields = [
            "id",
            "folio",
            "categoria",
            "descripcion",
            "archivo_adjunto",
            "fecha_creacion",
            "estado",
        ]

    def get_archivo_adjunto(self, obj):
        """Retorna la URL completa del archivo si existe"""
        if obj.archivo_adjunto:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.archivo_adjunto.url)
            return obj.archivo_adjunto.url
        return None
