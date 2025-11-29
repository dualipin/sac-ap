import environ
from pathlib import Path
from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DATABASE_ENGINE=(str, 'sqlite')
)

environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env('DJANGO_DEBUG')

# Configuración de cifrado
FERNET_KEY = env('FERNET_KEY')
SECURITY_PEPPER = SECRET_KEY
FERNET_KEYS = {
    'k1': FERNET_KEY,
}

FERNET_PRIMARY_KEY_ID = 'k1'

if not FERNET_KEYS or not SECURITY_PEPPER:
    raise ImproperlyConfigured("Las claves de cifrado no están configuradas correctamente.")

try:
    FERNET: str = FERNET_KEYS[FERNET_PRIMARY_KEY_ID]
    Fernet(FERNET.encode() if isinstance(FERNET, str) else FERNET)
except Exception as e:
    raise ImproperlyConfigured("La clave FERNET_KEY no es válida.") from e

# External API URLs
CURP_API_URL = env("CURP_API_URL")

# Allowed hosts
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'] if DEBUG else [])

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = env.int('EMAIL_PORT', 587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', 'tu_email@example.com')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', 'tu_contraseña')
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = f"SAC Macuspana <{EMAIL_HOST_USER}>"

# CORS settings
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

# User model
# AUTH_USER_MODEL = 'auths.User'

# REST Framework settings
REST_FRAMEWORK = {
    # "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # "DEFAULT_PERMISSION_CLASSES": [
    #     "rest_framework.permissions.IsAuthenticated"
    # ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "EXCEPTION_HANDLER": "apps.utils.exceptions.custom_exception_handler",
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_filters',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'simple_history',
    'apps.cuentas',
    'apps.auths',
    'apps.localidades',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware'
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_ENGINE = env('DATABASE_ENGINE')

if DATABASE_ENGINE == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": env("DATABASE_HOST", default="localhost"),
            "USER": env("DATABASE_USER", default="user"),
            "PASSWORD": env("DATABASE_PASSWORD", default="password"),
            "NAME": env("DATABASE_NAME", default="db_name"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "es-MX"

TIME_ZONE = "America/Mexico_City"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
