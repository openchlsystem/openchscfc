"""
Django settings for cfcbe project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
import warnings

# Suppress FutureWarning from torch.load in Whisper
warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hb(yb)v5&^t3^42-320z=zw_$agrp-4+%ss^90l+y=3ua@k$7$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['154.72.207.59','backend.bitz-itc.com', 'localhost', '0.0.0.0','127.0.0.1']

MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # my apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    

    
    # 'emailfeedback',
    'django_filters',


    # New Gateway Apps,
    'webhook_handler',
    'platform_adapters',
    'endpoint_integration',
    'shared',


    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cfcbe.urls'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

CORS_ALLOW_ALL_ORIGINS = True

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

WSGI_APPLICATION = 'cfcbe.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cors
CORS_ALLOW_CREDENTIALS = True

# Allow specific enable in production
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # For local development
    "http://localhost:5173",  # For local development
    "https://webform.bitz-itc.com",
]


CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-requested-with',
    'accept',
    'origin',
    'user-agent',
]


CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
PLATFORM_CONFIGS = {
    'webform': {
        'api_token': "19021977"
    },
    'whatsapp': {
        'verify_token': "19021977",
        'api_token': 'sci9de994iddqlmj8fv7r1js74',
        # 'app_secret': 'your-app-secret',
        # 'api_token': 'your-meta-api-token',
        'phone_number_id': '555567910973933',
        'client_id': '9517610311624041',
        'client_secret': '3bac93f1342c1c0fdbd6d755d515b5ae',
        'business_id': '101592599705197',
        'access_token': "EACHQN1W8JWkBO6DYzdQ1vrpTrGYttRX2CHc8tMAHyWz2ZCST4qTN7c5kiHEQ3SVxn2prZBp1XzHBAJZCzVY1fAEwltWl6mwS2XaZBA18VixvNdebJEzzei6AMlpn66YjUAf915ZASXH5h93730vZAR9bBUvs8oLi1ZA18viUqT2G5TAflvZA2NXIWvyAVDxXo5fg1phyCQZDZD"
    }
}



VERIFICATION_TOKEN = "19021977"

BEARER_TOKEN = "sci9de994iddqlmj8fv7r1js74"

# WhatsApp API Credentials
WHATSAPP_CLIENT_ID = "9517610311624041"
WHATSAPP_CLIENT_SECRET = "3bac93f1342c1c0fdbd6d755d515b5ae"
WHATSAPP_BUSINESS_ID = "101592599705197"
WHATSAPP_PHONE_NUMBER_ID = "555567910973933"

# Updated long-lived access token
WHATSAPP_ACCESS_TOKEN = "EACHQN1W8JWkBO6DYzdQ1vrpTrGYttRX2CHc8tMAHyWz2ZCST4qTN7c5kiHEQ3SVxn2prZBp1XzHBAJZCzVY1fAEwltWl6mwS2XaZBA18VixvNdebJEzzei6AMlpn66YjUAf915ZASXH5h93730vZAR9bBUvs8oLi1ZA18viUqT2G5TAflvZA2NXIWvyAVDxXo5fg1phyCQZDZD"

# WhatsApp API Base URL
WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"

# WhatsApp API Base URL
WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"



# Webhook Verification Token (If using webhooks)
WHATSAPP_WEBHOOK_VERIFY_TOKEN = "19021977"

# # Endpoint configuration
# ENDPOINT_CONFIG = {
#     'cases_endpoint': {
#         'url': 'https://demo-openchs.bitz-itc.com/helpline/api/cases/',
#         'auth_token': 'sci9de994iddqlmj8fv7r1js74',
#         'formatter': 'cases'
#     },
#     'messaging_endpoint': {
#         'url': 'https://demo-openchs.bitz-itc.com/helpline/api/msg/',
#         'auth_token': 'sci9de994iddqlmj8fv7r1js74',
#         'formatter': 'messaging'
#     }
# }

ENDPOINT_CONFIG = {
    'cases_endpoint': {
        'url': 'http://127.0.0.1/helpline/api/cases/',
        'auth_token': 'cli04pph08uuv3skdo287604on',
        'formatter': 'cases'
    },
    'messaging_endpoint': {
        'url': 'http://127.0.0.1/helpline/api/msg/',
        'auth_token': 'cli04pph08uuv3skdo287604on',
        'formatter': 'messaging'
    }
}


