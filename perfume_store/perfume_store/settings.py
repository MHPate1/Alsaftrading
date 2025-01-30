import os
from pathlib import Path
import environ

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY SETTINGS
DEBUG = False  # Set to False for production
SECRET_KEY = env('SECRET_KEY')  # Move to env variable

ALLOWED_HOSTS = [
    'giftoutlet.co.uk',
    'www.giftoutlet.co.uk',
    'alsaftrading-900247810812.europe-west1.run.app',
    '*',  # Temporarily add this for testing
]

CSRF_TRUSTED_ORIGINS = [
    'https://giftoutlet.co.uk',
    'https://www.giftoutlet.co.uk',
    'https://alsaftrading-900247810812.europe-west1.run.app',
]

# STRIPE SETTINGS
if DEBUG:
    STRIPE_PUBLIC_KEY = env('STRIPE_TEST_PUBLIC_KEY')
    STRIPE_SECRET_KEY = env('STRIPE_TEST_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = env('STRIPE_TEST_WEBHOOK_SECRET')
else:
    STRIPE_PUBLIC_KEY = env('STRIPE_LIVE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = env('STRIPE_LIVE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = env('STRIPE_LIVE_WEBHOOK_SECRET')

# SECURITY MIDDLEWARE SETTINGS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store.apps.StoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Above all other middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f'Gift Outlet <{env("EMAIL_HOST_USER")}>'
BUSINESS_EMAIL = EMAIL_HOST_USER

# STATIC FILES
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

ROOT_URLCONF = 'perfume_store.urls'
WSGI_APPLICATION = 'perfume_store.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'