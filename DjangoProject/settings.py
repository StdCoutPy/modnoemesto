
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import environ
import os

env = environ.Env(DEBUG=(bool, False))
# Читаем файл .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  env('DEBUG')

CSRF_TRUSTED_ORIGINS = env.list('TRUSTED_ORIGINS')
#ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
# `Ap`plication definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'chat',
    'orders',
    'users',
    'products',
    'content',
    'rest_framework',
]

JAZZMIN_SETTINGS = {
    "site_title": "Admin Panel",
    "site_header": "My Project",
    "site_brand": "Modnoe Mesto",
    "welcome_sign": "Добро пожаловать",
    "theme": "darkly",
}




MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DjangoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.categories_menu',
                'orders.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'DjangoProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "static_root"
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'




#LOGIN
# settings.py
AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGOUT_REDIRECT_URL = '/'


# Настройки email для Google
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True  # Используем TLS шифрование
EMAIL_HOST_USER = env('EMAIL_HOST_USER')  # Ваш Google email
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD') # Пароль приложения из шага 3
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # От кого будут письма
SERVER_EMAIL = EMAIL_HOST_USER  # Для системных уведомлений

# Для удобства разработки - разделяем режимы
if DEBUG:
    # В режиме разработки показываем письма в консоль
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    # На боевом сервере отправляем реальные письма
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Список админских email (для автоматического назначения прав админа)
ADMIN_EMAILS = env.list('ADMIN_EMAILS', default=['admin@modnoemesto.ru'])





#TG
TELEGRAM_BOT_TOKEN = env('TG_TOKEN')
TELEGRAM_BOT_NAME = env('TG_NAME')

# Укажи свой актуальный домен ngrok

# Чтобы Chrome не блокировал всплывающее окно
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

#Параметры для Freedom Pay Sandbox
PG_MERCHANT_ID = env('PG_MERCHANT_ID')
PG_KEY = env('PAYBOX_KEY')


#OPEN AI API
AI_API_KEY=env('AI_API_KEY')


#Доверие прокси (для CSRF): Чтобы Django понимал, что он за Nginx.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
