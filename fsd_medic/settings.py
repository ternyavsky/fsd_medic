import os.path
from datetime import timedelta
from pathlib import Path
from corsheaders.defaults import default_headers
from dotenv import load_dotenv

AUTH_USER_MODEL = "api.User"
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", os.environ.get("SECRET_KEY"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG_STATUS")

ALLOWED_HOSTS = [
    "*",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": ("rest_framework.pagination.LimitOffsetPagination"),
}
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "templates",
    "drf_yasg",
    "djangochannelsrestframework",
    "rest_framework",
    "debug_toolbar",
    "django_prometheus",
    "django_filters",
    "django_loki",
    "storages",
    "socketio",
    "corsheaders",
    "api.apps.ApiConfig",
    "social.apps.SocialConfig",
    "auth_user.apps.AuthUserConfig",
    "auth_doctor.apps.AuthDoctorConfig",
    "db.apps.DbConfig",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "api.middleware.open_access_middleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    # 'api.middleware.open_access_middleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]


CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:3001", "http://localhost:3001"]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    "http://127.0.0.1:3001",
    "http://192.168.0.14:3001",
    "http://172.17.0.1:3001",
    "http://localhost:3001",
)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "TOKEN_OBTAIN_SERIALIZER": "auth_user.serializers.CustomTokenObtainPairSerializer",
    "ALGORITHM": "HS256",
    "SIGNING_KEY": "Bearer",
    "VERIFYING_KEY": "Bearer",
}

ROOT_URLCONF = "fsd_medic.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "fsd_medic.wsgi.application"
ASGI_APPLICATION = "fsd_medic.asgi.application"

# LOGGING = {
#     'version': 1,
#     'formatters': {
#         'loki': {
#             'class': 'django_loki.LokiFormatter',  # required
#             # optional, default is logging.BASIC_FORMAT
#             'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] [%(funcName)s] %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',  # optional, default is '%Y-%m-%d %H:%M:%S'
#         },
#     },
#     'handlers': {
#         'loki': {
#             'level': 'DEBUG',  # required
#             'class': 'django_loki.LokiHttpHandler',  # required
#             'host': 'localhost',  # required, your grafana/Loki server host, e.g:192.168.57.242
#             'formatter': 'loki',  # required, loki formatter,
#             'port': 3100,  # optional, your grafana/Loki server port, default is 3100
#             'timeout': 0.5,  # optional, request Loki-server by http or https time out, default is 0.5
#             'protocol': 'http',  # optional, Loki-server protocol, default is http
#             'source': 'Loki',  # optional, label name for Loki, default is Loki
#             'src_host': 'localhost',  # optional, label name for Loki, default is localhost
#             'tz': 'UTC',  # optional, timezone for formatting timestamp, default is UTC, e.g:Asia/Shanghai
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['loki'],
#             'level': 'INFO',
#             'propagate': False,
#         }
#     },
# }
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    }
}
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
        #'NAME': "sys",
        "NAME": os.getenv("DB_NAME"),
        # 'USER': "root",
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        #'PASSWORD': "root",
        "PORT": os.getenv("DB_PORT"),
        #'HOST': "172.17.0.1" ,
        "HOST": os.getenv("DB_HOST"),
        "OPTIONS": {"sql_mode": os.getenv("DB_SQL_MODE")},
    }
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BACKEND")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "172.17.0.1:11211",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("172.17.0.1", 6379)],
        },
    },
}
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"
USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# EMAIL
EMAIL_USE_TLS = os.getenv("EM_USE_TLS")
EMAIL_HOST = os.getenv("EM_HOST")
EMAIL_HOST_USER = os.getenv("EM_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EM_HOST_PASSWORD")
EMAIL_PORT = os.getenv("EM_PORT")

# S3 BUCKET
AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = f'https://{os.getenv("S3_DOMAIN")}'
AWS_S3_REGION_NAME = os.getenv("S3_REGION")
AWS_LOCATION_STATIC = "static"
AWS_LOCATION_MEDIA = "media"
AWS_DEFAULT_ACL = os.getenv("S3_ACL")


STATIC_URL = "https://%s/%s/" % (AWS_S3_ENDPOINT_URL, AWS_LOCATION_STATIC)
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = "https://%s/%s/" % (AWS_S3_ENDPOINT_URL, AWS_LOCATION_MEDIA)
DEFAULT_FILE_STORAGE = "fsd_medic.storage_backends.MediaStorage"

GEOIP_PATH = os.path.join(BASE_DIR, "geoip/")
PHONE_VERIFICATION = {
    "BACKEND": "phone_verify.backends.twilio.TwilioBackend",
    "OPTIONS": {
        "SID": "fake",
        "SECRET": "fake",
        "FROM": "+6283899634806",
        "SANDBOX_TOKEN": "123456",
    },
    "TOKEN_LENGTH": 6,
    "MESSAGE": "Welcome to {app}! Please use security code {security_code} to proceed.",
    "APP_NAME": "Phone Verify",
    "SECURITY_CODE_EXPIRATION_TIME": 3600,  # In seconds only
    "VERIFY_SECURITY_CODE_ONLY_ONCE": False,
    # If False, then a security code can be used multiple times for verification
}
