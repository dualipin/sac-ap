from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from .constants import ROLES_CHOICES


class UsuarioManager(BaseUserManager):
    def create_user(self, usuario: str | None, rol="ciudadano", password=None):
        if not usuario:
            raise ValueError("El usuario debe tener un nombre de usuario")
        user = self.model(usuario=usuario, rol=rol)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, usuario, rol="admin", password=None):
        user = self.create_user(usuario, rol, password)
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):
    usuario = models.CharField(max_length=255, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES_CHOICES)

    objects = UsuarioManager()

    USERNAME_FIELD = "usuario"
