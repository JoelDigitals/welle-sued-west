"""
Django-Settings für das Projekt "Welle Süd-West".

Für den lokalen Start reichen die Standardwerte. Für einen echten Live-Betrieb
unbedingt SECRET_KEY, DEBUG und ALLOWED_HOSTS anpassen (siehe README.md).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sicherheit --------------------------------------------------------
# SECRET_KEY und DEBUG kommen aus Umgebungsvariablen, damit auf Render kein
# unsicherer Default landet. Lokal ohne gesetzte Variablen bleibt das
# Verhalten wie bisher (Debug an, Platzhalter-Key).
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'django-insecure-bitte-vor-dem-live-betrieb-aendern-!!!'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Render setzt RENDER_EXTERNAL_HOSTNAME automatisch auf die *.onrender.com-
# Domain des Service - die wird hier übernommen, damit ALLOWED_HOSTS nicht
# von Hand gepflegt werden muss.
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- Externe Player-/Metadaten-Quelle -----------------------------------
# Zentral an einer Stelle konfiguriert, damit sie sich leicht austauschen
# lässt (z. B. wenn das Studio-Backend einmal umzieht).
RADIO_STUDIO_BASE_URL = 'https://welle-sued-west-studio.onrender.com'
RADIO_PLAYER_EMBED_URL = f'{RADIO_STUDIO_BASE_URL}/player'
RADIO_NOWPLAYING_API_URL = f'{RADIO_STUDIO_BASE_URL}/api/public/nowplaying'
RADIO_LIVE_STREAM_URL = f'{RADIO_STUDIO_BASE_URL}/live-stream'
RADIO_HOTLINE_API_URL = f'{RADIO_STUDIO_BASE_URL}/api/public/hotline'
RADIO_AD_REQUESTS_API_URL = f'{RADIO_STUDIO_BASE_URL}/api/public/ad-requests'
RADIO_TRAFFIC_API_URL = f'{RADIO_STUDIO_BASE_URL}/api/public/traffic-overview'
RADIO_NEWS_API_URL = f'{RADIO_STUDIO_BASE_URL}/api/public/news-page'

# --- Apps ---------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'radio',
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

ROOT_URLCONF = 'wellesuedwest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wellesuedwest.wsgi.application'

# --- Datenbank ------------------------------------------------------------
# Standardmäßig SQLite - für den Start völlig ausreichend, kein Server nötig.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
