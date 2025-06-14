from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import redis
from urllib.parse import urlparse

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Allow all hosts for simplicity
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'cloudinary_storage',
    'cloudinary',
    
    # Local apps
    'accounts',
    'music',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'boomboxd.urls'

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

WSGI_APPLICATION = 'boomboxd.wsgi.application'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Static files configuration
if DEBUG:
    # Development: Django serves static files directly from these directories
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'staticfiles'),  # Our React build files
    ]
    # Don't set STATIC_ROOT in development
else:
    # Production: collectstatic copies files to STATIC_ROOT  
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_DIRS = []

# Cloudinary configuration for django-cloudinary-storage
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Use Cloudinary for media files
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Media files (User uploads) - fallback for development
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Cache Configuration
# Use Redis if available (production), fall back to dummy cache (development/Vercel)
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL:
    # Parse Redis URL for connection details
    redis_url = urlparse(REDIS_URL)
    
    # Redis Cloud configuration
    redis_options = {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        'CONNECTION_POOL_KWARGS': {
            'retry_on_timeout': True,
            'retry_on_error': [redis.ConnectionError, redis.TimeoutError],
            'health_check_interval': 30,
        }
    }
    
    # Ensure Redis connection is available at startup
    try:
        from django.core.cache import cache
        cache.get('test_connection')
        print("Redis connection successful")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        print("Falling back to database cache")
    
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': redis_options,
            'KEY_PREFIX': 'boomboxd',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }
else:
    # Fallback to database cache for development or when Redis isn't available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        }
    }

# Session engine (use cache if available)
if REDIS_URL:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# CORS - Allow all origins for development simplicity
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Development-friendly settings (no SSL required)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Discogs API
DISCOGS_API_URL = "https://api.discogs.com"
DISCOGS_CONSUMER_KEY = os.getenv('DISCOGS_CONSUMER_KEY')
DISCOGS_CONSUMER_SECRET = os.getenv('DISCOGS_CONSUMER_SECRET')
DISCOGS_TOKEN = os.getenv('DISCOGS_TOKEN', DISCOGS_CONSUMER_KEY)

 