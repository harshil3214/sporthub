"""
Django settings for config project.
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w-snbkgjhr!9so08_ub&v@n0b%1m29#71*!*cg0n(gcqp%i)ui'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your Apps
    'core',
    'cricket',
    'football',
    'volleyball',
]

# Optional: Background Tasks & Automation (Celery Beat)
try:
    import django_celery_beat  # noqa: F401
    INSTALLED_APPS.append('django_celery_beat')
except ModuleNotFoundError:
    pass

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # XFrameOptions is handled via X_FRAME_OPTIONS setting below 
    # to allow YouTube embeds while maintaining security.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'core.middleware.LoginRequiredMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # Set for Indian Standard Time
USE_I18N = True
USE_TZ = True
USE_L10N = False 

# Date/Time Formatting for Admin
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = 'Y-m-d H:i'

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "core" / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media Files (Team Logos, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication Redirects
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = 'home_dashboard'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- VIDEO & SECURITY FIXES ---
# Allows YouTube videos to be embedded and played on your site
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# --- CELERY SETTINGS ---
# Points Celery to your local Redis server
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
# Stores task results in the Django database (requires django-db result backend)
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

# Enables the Database-backed scheduler for Periodic Tasks (Admin-friendly)
try:
    import django_celery_beat  # noqa: F401
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
except ModuleNotFoundError:
    pass