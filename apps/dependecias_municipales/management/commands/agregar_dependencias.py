import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection
from apps.dependecias_municipales.models import DependenciaMunicipal


class Command(BaseCommand):
    help = 'Carga dependencias municipales desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('ruta', type=str, help='Ruta al archivo CSV con las dependencias municipales')

    def handle(self, *args, **options):
        ruta = options['ruta']

        self.stdout.write(self.style.NOTICE(f'Cargando archivo: {ruta}'))

        # Leer el archivo CSV
        df = pd.read_csv(ruta, dtype=str)

        total = len(df)
        self.stdout.write(self.style.WARNING(f'Registros en el archivo: {total}'))

        # Limpiar tabla antes de insertar
        try:
            DependenciaMunicipal.objects.all().delete()
        except Exception:
            self.stdout.write(self.style.NOTICE(f'Error al limpiar la tabla de dependencias municipales.'))

            with connection.cursor() as cursor:
                cursor.execute(f'DELETE FROM {DependenciaMunicipal._meta.db_table}')

            raise

        # Convertir DataFrame a objetos DependenciaMunicipal
        dependencias = [
            DependenciaMunicipal(
                id=row['id'],
                nombre=row['nombre'],
                descripcion=row.get('descripcion', ''),
                tipo=row.get('tipo', 'departamento'),
            )
            for _, row in df.iterrows()
        ]

        # Guardar por lotes
        try:
            DependenciaMunicipal.objects.bulk_create(dependencias, batch_size=300)
        except Exception:
            self.stdout.write(self.style.ERROR(f'Error al crear dependencias municipales.'))
