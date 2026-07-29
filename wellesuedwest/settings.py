"""
Django-Settings für das Projekt "Welle Süd-West".

Für den lokalen Start reichen die Standardwerte. Für einen echten Live-Betrieb
unbedingt SECRET_KEY, DEBUG und ALLOWED_HOSTS anpassen (siehe README.md).
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sicherheit --------------------------------------------------------
# WICHTIG: Vor dem Live-Betrieb einen eigenen, geheimen Wert setzen und
# NICHT im Repository speichern (z. B. über eine Umgebungsvariable laden).
SECRET_KEY = 'django-insecure-bitte-vor-dem-live-betrieb-aendern-!!!'

DEBUG = True

ALLOWED_HOSTS = ['*']

# --- Externe Player-/Metadaten-Quelle -----------------------------------
# Zentral an einer Stelle konfiguriert, damit sie sich leicht austauschen
# lässt (z. B. wenn das Studio-Backend einmal umzieht).
RADIO_STUDIO_BASE_URL = 'https://welle-sued-west-studio.onrender.com'
RADIO_PLAYER_EMBED_URL = f'{RADIO_STUDIO_BASE_URL}/player'
RADIO_NOWPLAYING_API_URL = f'{RADIO_STUDIO_BASE_URL}/api/public/nowplaying'
RADIO_LIVE_STREAM_URL = f'{RADIO_STUDIO_BASE_URL}/live-stream'

# --- Apps ---------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'radio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
