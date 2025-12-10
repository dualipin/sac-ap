import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection
import re
from apps.autenticacion.models import Usuario
from apps.dependecias_municipales.models import DependenciaMunicipal
from apps.funcionarios.models import Funcionario


class Command(BaseCommand):
    help = 'Carga funcionarios desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('ruta', type=str, help='Ruta al archivo CSV con los funcionarios')

    def handle(self, *args, **options):
        ruta = options['ruta']

        self.stdout.write(self.style.NOTICE(f'Cargando archivo: {ruta}'))

        # Leer el archivo CSV
        df = pd.read_csv(ruta, dtype=str)

        # --- CORRECCIÓN PRINCIPAL ---
        # Convertir todos los valores NaN (float) a cadenas vacías ('')
        df = df.fillna('')
        # ----------------------------

        total = len(df)
        self.stdout.write(self.style.WARNING(f'Registros en el archivo: {total}'))

        # Limpiar tabla antes de insertar
        try:
            Funcionario.objects.all().delete()
        except Exception:
            self.stdout.write(
                self.style.NOTICE(f'Error al limpiar la tabla de funcionarios, intentando truncate manual...'))
            with connection.cursor() as cursor:
                cursor.execute(f'DELETE FROM {Funcionario._meta.db_table}')

        # Definir la función de correo (ligeramente mejorada para ser defensiva)
        def correo_temporal(nombre, apellido):
            # Aseguramos que sean strings por si acaso
            nombre = str(nombre) if nombre else ""
            apellido = str(apellido) if apellido else ""

            nombre_limpio = re.sub(r'[^a-zA-Z\s]', '', nombre)
            nombre_sin_espacios = nombre_limpio.lower().replace(' ', '')

            apellido_limpio = re.sub(r'[^a-zA-Z]', '', apellido)
            apellido_normalizado = apellido_limpio.lower()

            return f"{nombre_sin_espacios}.{apellido_normalizado}@macuspana.gob.mx"

        funcionarios = []

        for _, row in df.iterrows():
            # Obtener datos (ya no serán NaN gracias al fillna)
            nombre = row['nombre']
            apellido_paterno = row.get('apellido_paterno', '')
            correo = row.get('correo_electronico')

            # Verificar si el correo está vacío (string vacío)
            if not correo:
                correo = correo_temporal(nombre, apellido_paterno)

            try:
                # Usamos get_or_create para evitar error si el usuario ya existe por corridas previas fallidas
                usuario, created = Usuario.objects.get_or_create(
                    usuario=correo,
                    defaults={
                        'rol': 'funcionario'
                    }
                )
                usuario.set_password('temporal')
                usuario.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al gestionar usuario {correo}: {str(e)}'))
                continue

            try:
                dependencia_id = row['dependencia_id']
                # Validar que sea un número válido antes de buscar
                if not dependencia_id or not str(dependencia_id).isdigit():
                    self.stdout.write(self.style.ERROR(f'ID Dependencia inválido para {nombre}'))
                    continue

                dependencia = DependenciaMunicipal.objects.get(id=dependencia_id)

                nombre_completo = f"{nombre} {apellido_paterno} {row.get('apellido_materno', '')}".strip()

                funcionario = Funcionario(
                    nombre_completo=nombre_completo,
                    sexo=row.get('sexo', 'M'),
                    cargo=row.get('puesto', 'responsable'),
                    dependencia=dependencia,
                    correo=correo,
                    telefono=row.get('telefono', ''),
                    usuario=usuario,
                )
                funcionarios.append(funcionario)
            except DependenciaMunicipal.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Dependencia ID {dependencia_id} no encontrada.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error procesando fila {nombre}: {str(e)}'))

        # Guardar por lotes
        try:
            Funcionario.objects.bulk_create(funcionarios, batch_size=300)
            self.stdout.write(self.style.SUCCESS(f'Éxito. Se crearon {len(funcionarios)} funcionarios.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error en bulk_create: {str(e)}'))
