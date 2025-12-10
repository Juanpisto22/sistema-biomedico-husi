"""
Configuración de Django para el proyecto de rondas biomédicas.
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-!$-ky%qw3yii2&+nq@qvij*dt3ixjhll8k^ajmc7(3*(1af#r9')

DEBUG = True

ALLOWED_HOSTS = [
    "sistema-biomedico-husi-production.up.railway.app",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://sistema-biomedico-husi-production.up.railway.app",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rondas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestion_biomedica.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_biomedica.wsgi.application'

BASE_DIR = Path(__file__).resolve().parent.parent

import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=False
    )
}



# Fallback a SQLite para desarrollo local
if not os.environ.get('PGHOST'):
    # Verificar si queremos usar SQL Server
    USE_SQLSERVER = os.environ.get('USE_SQLSERVER', 'False') == 'True'
    
    if USE_SQLSERVER:
        # Configuración para SQL Server
        DATABASES = {
            'default': {
                'ENGINE': 'mssql',
                'NAME': 'BIOMEDICADES',
                'USER': 'AdminBiomedicaAPP',
                'PASSWORD': 'AdminBiomedicaAPPX',
                'HOST': 'WINDFTIB002\\MDM1',
                'PORT': '',
                'OPTIONS': {
                    'driver': 'ODBC Driver 17 for SQL Server',
                    'extra_params': 'TrustServerCertificate=yes',
                },
            }
        }
    else:
        # SQLite para desarrollo local (por defecto)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

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

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuración de Whitenoise para archivos estáticos
# En desarrollo (DEBUG=True) usar el storage por defecto para que los
# archivos estáticos nuevos se sirvan sin ejecutar collectstatic.
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (firmas, archivos subidos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'panel_principal'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

