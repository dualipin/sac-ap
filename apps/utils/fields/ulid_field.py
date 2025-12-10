from django.db import models
import ulid


class UlidField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('primary_key', True)
        kwargs.setdefault('max_length', 26)
        kwargs.setdefault('default', self.generate_ulid)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Elimina valores por defecto para evitar migraciones innecesarias
        kwargs.pop('primary_key', None)
        kwargs.pop('default', None)
        kwargs.pop('max_length', None)
        kwargs.pop('editable', None)
        return name, path, args, kwargs

    @staticmethod
    def generate_ulid():
        return str(ulid.ULID())
