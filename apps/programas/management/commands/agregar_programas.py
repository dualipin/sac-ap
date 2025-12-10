from apps.programas.models import Programa, DependenciaMunicipal
from django.core.management.base import BaseCommand
from django.db import connection

# Lista de programas para crear
programas_data = [
    {
        "titulo": "Apoyo Alimentario 'Nutriendo Familias'",
        "descripcion": "Entrega bimestral de despensas básicas a familias en situación de vulnerabilidad y adultos mayores.",
        "requisitos": {
            "edad_minima": 60,
            "documentos": ["INE", "Comprobante de domicilio", "Estudio socioeconómico"],
            "prioridad": "Alta"
        },
        "dependencia_id": 19  # COORDINACIÓN DEL SISTEMA DIF
    },
    {
        "titulo": "Becas a la Excelencia Académica",
        "descripcion": "Estímulo económico para estudiantes de nivel básico y medio superior con promedio superior a 9.0.",
        "requisitos": {
            "promedio_minimo": 9.0,
            "documentos": ["Boleta de calificaciones", "Constancia de estudios", "INE del tutor"],
            "nivel": ["Primaria", "Secundaria", "Preparatoria"]
        },
        "dependencia_id": 9  # DIRECCION DE EDUCACION CULTURA Y RECREACION
    },
    {
        "titulo": "Emprende Macuspana",
        "descripcion": "Capacitación y microcréditos para nuevos emprendedores locales y artesanos.",
        "requisitos": {
            "tipo_apoyo": "Capacitación y Financiamiento",
            "documentos": ["Plan de negocios simple", "INE", "RFC"],
            "residencia": "Mínimo 1 año en el municipio"
        },
        "dependencia_id": 7  # DIRECCIÓN DE FOMENTO ECONOMICO Y TURISMO
    },
    {
        "titulo": "Programa 'Bacheo Emergente'",
        "descripcion": "Reparación intensiva de calles y avenidas principales reportadas por la ciudadanía.",
        "requisitos": {
            "canal_reporte": ["App Móvil", "Ventanilla Única"],
            "evidencia": "Foto del bache y ubicación GPS"
        },
        "dependencia_id": 8  # DIRECCIÓN DE OBRAS, ORDENAMIENTO TERRITORIAL
    },
    {
        "titulo": "Mujer Segura y Empoderada",
        "descripcion": "Servicios gratuitos de psicología, asesoría legal y talleres de autoempleo para mujeres.",
        "requisitos": {
            "poblacion_objetivo": "Mujeres mayores de 18 años",
            "costo": "Gratuito",
            "documentos": ["Identificación oficial"]
        },
        "dependencia_id": 14  # DIRECCIÓN DE ATENCION A LAS MUJERES
    },
    {
        "titulo": "Campaña de Regularización 'Ponte al Corriente'",
        "descripcion": "Descuentos en multas y recargos para usuarios con adeudos en el servicio de agua potable.",
        "requisitos": {
            "documentos": ["Recibo de agua anterior", "INE"],
            "vigencia": "Octubre - Diciembre",
            "descuento": "Hasta 50% en recargos"
        },
        "dependencia_id": 16  # SAPAM
    },
    {
        "titulo": "Macuspana Verde",
        "descripcion": "Jornadas de reforestación urbana y donación de árboles frutales a escuelas y parques.",
        "requisitos": {
            "solicitante": ["Escuelas", "Comités de Vecinos"],
            "compromiso": "Carta compromiso de cuidado y riego"
        },
        "dependencia_id": 15  # DIRECCIÓN DE PROTECCION AMBIENTAL
    },
    {
        "titulo": "Impulso al Campo",
        "descripcion": "Entrega subsidiada de semillas, fertilizantes y herramientas menores para pequeños productores.",
        "requisitos": {
            "documentos": ["Certificado parcelario", "INE"],
            "hectareas_maximas": 5
        },
        "dependencia_id": 6  # DIRECCIÓN DE DESARROLLO
    },
    {
        "titulo": "Red Vecinal 'Vecino Vigilante'",
        "descripcion": "Organización de comités vecinales con enlace directo a seguridad pública y alarmas vecinales.",
        "requisitos": {
            "participantes_minimos": 10,
            "zona": "Urbana y Suburbana",
            "reuniones": "Mensuales"
        },
        "dependencia_id": 20  # DIRECCION DE SEGURIDAD PUBLICA
    },
    {
        "titulo": "Techo Firme",
        "descripcion": "Construcción de techos de lámina o concreto para viviendas en zonas de alta marginación.",
        "requisitos": {
            "estudio_socioeconomico": True,
            "propiedad": "Acreditación de posesión legal",
            "prioridad": "Madres solteras"
        },
        "dependencia_id": 17  # INSTITUTO DE VIVIENDA DE MACUSPANA
    },
    {
        "titulo": "Educación Vial Escolar",
        "descripcion": "Cursos y prácticas de educación vial impartidos en escuelas primarias.",
        "requisitos": {
            "solicitud": "Oficio del director de la escuela",
            "espacio": "Patio cívico disponible"
        },
        "dependencia_id": 11  # DIRECCIÓN DE TRANSITO
    },
    {
        "titulo": "Prevención Invernal y Lluvias",
        "descripcion": "Identificación de refugios temporales y limpieza de drenes pluviales.",
        "requisitos": {
            "tipo": "Preventivo",
            "zonas_riesgo": ["Zonas bajas", "Márgenes de ríos"]
        },
        "dependencia_id": 18  # COORDINACIÓN DE PROTECCIÓN CIVIL
    },
    {
        "titulo": "Domingos Culturales",
        "descripcion": "Espacios para artistas locales, música y danza en el parque central.",
        "requisitos": {
            "registro_artistas": "Previo en DECUR",
            "entrada": "Libre"
        },
        "dependencia_id": 9  # DIRECCION DE EDUCACION CULTURA Y RECREACION
    },
    {
        "titulo": "Certeza Jurídica Patrimonial",
        "descripcion": "Asesoría para la regularización de predios y testamentos a bajo costo.",
        "requisitos": {
            "convenio": "Notarías locales",
            "documentos_base": ["Posesión pacífica", "INE"]
        },
        "dependencia_id": 12  # DIRECTOR JURIDICO
    },
    {
        "titulo": "Audiencias Públicas",
        "descripcion": "Atención directa del Presidente Municipal y Directores a la ciudadanía.",
        "requisitos": {
            "fichas": "Se entregan a las 8:00 AM",
            "limite_diario": 50
        },
        "dependencia_id": 13  # DIRECCIÓN DE ATENCION CIUDADANA
    }
]


class Command(BaseCommand):
    help = 'Agrega programas municipales predefinidos a la base de datos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando la creación de programas municipales...'))

        # Limpiar tabla antes de insertar
        try:
            Programa.objects.all().delete()
        except Exception:
            self.stdout.write(
                self.style.NOTICE(f'Error al limpiar la tabla de programas, intentando truncate manual...'))
            with connection.cursor() as cursor:
                cursor.execute(f'DELETE FROM {Programa._meta.db_table}')

        # Loop para crear los objetos
        for p in programas_data:
            # Obtenemos la instancia de la dependencia (asumiendo que los IDs existen)
            try:
                dependencia = DependenciaMunicipal.objects.get(pk=p['dependencia_id'])

                Programa.objects.create(
                    titulo=p['titulo'],
                    descripcion=p['descripcion'],
                    requisitos=p['requisitos'],
                    dependencia_municipal=dependencia
                )
                self.stdout.write(self.style.SUCCESS(f"Programa '{p['titulo']}' creado exitosamente."))
            except DependenciaMunicipal.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Error: La dependencia con ID {p['dependencia_id']} no existe."))

        self.stdout.write(self.style.NOTICE('Proceso de creación de programas finalizado.'))
