"""
Constantes centralizadas para roles de usuario.
Single source of truth para roles en todo el proyecto.
"""

# Constantes de roles
ADMIN = "admin"
FUNCIONARIO = "funcionario"
CIUDADANO = "ciudadano"

# Diccionario para acceso programático
ROLES = {
    "ADMIN": ADMIN,
    "FUNCIONARIO": FUNCIONARIO,
    "CIUDADANO": CIUDADANO,
}

# Choices para modelo Django
ROLES_CHOICES = [
    (ADMIN, "Administrador"),
    (FUNCIONARIO, "Funcionario"),
    (CIUDADANO, "Ciudadano"),
]

# Grupos de roles para validaciones comunes
ROLES_ADMIN = [ADMIN]
ROLES_FUNCIONARIOS = [ADMIN, FUNCIONARIO]
ROLES_CIUDADANOS = [CIUDADANO]
ROLES_AUTHENTICATED = [ADMIN, FUNCIONARIO, CIUDADANO]

# Descripción de roles para documentación
ROLES_DESCRIPTIONS = {
    ADMIN: "Administrador del sistema con acceso completo a todas las funcionalidades",
    FUNCIONARIO: "Funcionario municipal que puede gestionar solicitudes y programas",
    CIUDADANO: "Ciudadano que puede crear solicitudes y ver estado de sus trámites",
}
