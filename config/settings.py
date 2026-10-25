import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Lightweight .env support without requiring an extra package.
env_file = BASE_DIR / '.env'
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'development-only-secret-autoledger-bd-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', '1') == '1'
if not DEBUG and (SECRET_KEY in {'development-only-secret-autoledger-bd-change-me', 'change-this-in-production-use-a-long-random-key'} or len(SECRET_KEY) < 48):
    raise RuntimeError('Set a unique, randomly generated DJANGO_SECRET_KEY (48+ characters) before running with DJANGO_DEBUG=0.')
ALLOWED_HOSTS = [s.strip() for s in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if s.strip()]
CSRF_TRUSTED_ORIGINS = [s.strip() for s in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if s.strip()]

INSTALLED_APPS = [
    'ledger.admin_config.SuperuserAdminConfig', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'django.contrib.humanize',
    'ledger',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ledger.middleware.SessionExpiryMiddleware',
    'ledger.middleware.DriverAccessMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'ledger.context.language_context',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'

if os.getenv('DB_HOST'):
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'autoledger'),
        'USER': os.getenv('DB_USER', 'autoledger'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }}
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_IDLE_TIMEOUT = 5 * 60
PUSH_NOTIFY_SUPERUSERS = True
WEBPUSH_PRIVATE_KEY = os.getenv('WEBPUSH_PRIVATE_KEY', str(BASE_DIR / '.secrets/webpush-private.pem'))
WEBPUSH_PUBLIC_KEY = os.getenv('WEBPUSH_PUBLIC_KEY', '')
if not WEBPUSH_PUBLIC_KEY and (BASE_DIR / '.secrets/webpush-public.txt').exists():
    WEBPUSH_PUBLIC_KEY = (BASE_DIR / '.secrets/webpush-public.txt').read_text().strip()
WEBPUSH_SUBJECT = os.getenv('WEBPUSH_SUBJECT', 'mailto:admin@example.com')
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', '1') == '1'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
