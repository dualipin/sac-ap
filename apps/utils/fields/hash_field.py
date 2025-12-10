from django.db import models


class HashField(models.CharField):
    """
    Campo personalizado para almacenar hashes.
    Configurado como CharField con longitud fija de 64 caracteres.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 64)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('db_index', True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop('max_length', None)
        kwargs.pop('editable', None)
        kwargs.pop('db_index', None)
        return name, path, args, kwargs
