import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection
from apps.localidades.models import Localidad


class Command(BaseCommand):
    help = 'Carga localidades desde el archivo CPdescarga.txt'

    def add_arguments(self, parser):
        parser.add_argument('ruta', type=str, help='Ruta al archivo de correos de Mexico')

    def handle(self, *args, **options):
        ruta = options['ruta']

        self.stdout.write(self.style.NOTICE(f'Cargando archivo: {ruta}'))

        # Leer el archivo con la codificación correcta
        df = pd.read_csv(ruta, encoding='latin1', sep='|', dtype=str)

        # Seleccionar solo las columnas necesarias
        df = df[['d_codigo', 'd_asenta', 'D_mnpio', 'd_estado', 'd_tipo_asenta']]

        # Renombrar columnas para coincidir con el modelo
        df.columns = ['codigo_postal', 'colonia', 'municipio', 'estado', 'tipo']

        # Eliminar duplicados (muchos CP se repiten por tipo)
        df = df.drop_duplicates()

        total = len(df)
        self.stdout.write(self.style.WARNING(f'Registros únicos: {total}'))

        # Limpiar tabla antes de insertar
        try:
            Localidad.objects.all().delete()
        except Exception:
            self.stdout.write(self.style.NOTICE(f'Error al limpiar la tabla de localidades.'))

            with connection.cursor() as cursor:
                cursor.execute(f'DELETE FROM {Localidad._meta.db_table}')

            raise

        # Convertir DataFrame a objetos Localidad
        localidades = [
            Localidad(
                codigo_postal=row['codigo_postal'],
                colonia=row['colonia'],
                municipio=row['municipio'],
                estado=row['estado'],
                tipo=row['tipo'],
            )
            for _, row in df.iterrows()
        ]

        # Guardar por lotes
        try:
            Localidad.objects.bulk_create(localidades, batch_size=300)
        except Exception:
            self.stdout.write(self.style.ERROR(f'Error al crear localidades.'))
        # Localidad.objects.bulk_create(localidades, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(f'✅ {total} localidades cargadas correctamente.'))
