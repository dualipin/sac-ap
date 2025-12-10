from django.core.management import BaseCommand
from django.db import connection

from apps.dependecias_municipales.models import DependenciaMunicipal
from apps.solicitudes.models import Categoria

categorias_data = [
    # Dirección de Obras (ID 8)
    {
        "nombre": "Bacheo y Pavimentación",
        "descripcion": "Reporte de baches, solicitud de pavimentación y mantenimiento de calles.",
        "dependencia_id": 8
    },
    {
        "nombre": "Alumbrado Público",
        "descripcion": "Reparación de luminarias fundidas y mantenimiento de postes de luz.",
        "dependencia_id": 8
    },
    {
        "nombre": "Recolección de Basura",
        "descripcion": "Reportes sobre fallas en el servicio de recolección de residuos sólidos.",
        "dependencia_id": 8
    },
    {
        "nombre": "Mantenimiento de Parques",
        "descripcion": "Solicitud de limpieza y mantenimiento de parques, jardines y áreas verdes.",
        "dependencia_id": 8
    },
    {
        "nombre": "Licencias de Construcción",
        "descripcion": "Trámites y permisos para obras de construcción o ampliación de viviendas.",
        "dependencia_id": 8
    },

    # Agua Potable (ID 16)
    {
        "nombre": "Fugas de Agua Potable",
        "descripcion": "Reporte de desperdicio de agua en tuberías de la red pública.",
        "dependencia_id": 16
    },
    {
        "nombre": "Desazolve de Drenaje",
        "descripcion": "Limpieza de alcantarillas y mantenimiento de la red de drenaje.",
        "dependencia_id": 16
    },
    {
        "nombre": "Contratos y Pagos de Agua",
        "descripcion": "Atención para nuevos contratos, reconexiones o aclaraciones de saldo.",
        "dependencia_id": 16
    },

    # Tránsito (ID 11)
    {
        "nombre": "Señalamientos Viales",
        "descripcion": "Solicitud de pintura de pasos peatonales, topes y señales de tránsito.",
        "dependencia_id": 11
    },
    {
        "nombre": "Accidentes de Tránsito",
        "descripcion": "Reporte y seguimiento de incidentes viales ocurridos en el municipio.",
        "dependencia_id": 11
    },

    # Protección Civil (ID 18)
    {
        "nombre": "Emergencias y Riesgos",
        "descripcion": "Reporte de situaciones de riesgo inminente, inundaciones o incendios.",
        "dependencia_id": 18
    },

    # Seguridad Pública (ID 20)
    {
        "nombre": "Vigilancia Preventiva",
        "descripcion": "Solicitud de rondines policiales y mayor presencia en colonias.",
        "dependencia_id": 20
    },
    {
        "nombre": "Denuncia Anónima",
        "descripcion": "Canal para reportar actividades sospechosas de manera anónima.",
        "dependencia_id": 20
    },

    # Protección Ambiental (ID 15)
    {
        "nombre": "Poda y Tala de Árboles",
        "descripcion": "Permisos y denuncias relacionadas con la tala indebida de árboles.",
        "dependencia_id": 15
    },
    {
        "nombre": "Contaminación y Ruido",
        "descripcion": "Reportes por quema de basura, ruido excesivo o vertidos contaminantes.",
        "dependencia_id": 15
    },

    # Atención Ciudadana (ID 13)
    {
        "nombre": "Audiencia con Funcionarios",
        "descripcion": "Solicitud de citas para hablar con directores o el presidente municipal.",
        "dependencia_id": 13
    },
    {
        "nombre": "Quejas y Sugerencias",
        "descripcion": "Buzón general para comentarios sobre el desempeño del ayuntamiento.",
        "dependencia_id": 13
    },

    # Contraloría (ID 5)
    {
        "nombre": "Denuncias a Servidores Públicos",
        "descripcion": "Quejas por mala atención o actos indebidos de funcionarios municipales.",
        "dependencia_id": 5
    },

    # Fomento Económico (ID 7)
    {
        "nombre": "Apoyo a Emprendedores",
        "descripcion": "Información sobre créditos y programas para pequeños negocios.",
        "dependencia_id": 7
    },

    # Educación y Cultura (ID 9)
    {
        "nombre": "Actividades Culturales",
        "descripcion": "Información y gestión de talleres, eventos y espacios culturales.",
        "dependencia_id": 9
    }
]


class Command(BaseCommand):
    help = 'Agrega categorías predeterminadas al sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando la creación de categorías...'))

        # Limpiar tabla antes de insertar
        try:
            Categoria.objects.all().delete()
        except Exception:
            self.stdout.write(
                self.style.NOTICE(f'Error al limpiar la tabla de categorías, intentando truncate manual...'))
            with connection.cursor() as cursor:
                cursor.execute(f'DELETE FROM {Categoria._meta.db_table}')

        # Loop para crear los objetos
        for c in categorias_data:
            try:
                dependencia = DependenciaMunicipal.objects.get(pk=c['dependencia_id'])

                Categoria.objects.create(
                    nombre=c['nombre'],
                    descripcion=c['descripcion'],
                    dependencia_municipal=dependencia
                )
                self.stdout.write(self.style.SUCCESS(f"Categoría '{c['nombre']}' creada exitosamente."))
            except DependenciaMunicipal.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Error: La dependencia con ID {c['dependencia_id']} no existe."))
