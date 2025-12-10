import uuid
from django.db import models


class UUIDField(models.UUIDField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('primary_key', True)
        kwargs.setdefault('default', uuid.uuid4)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop('primary_key', None)
        kwargs.pop('default', None)
        kwargs.pop('editable', None)
        return name, path, args, kwargs
