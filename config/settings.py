from pathlib import Path


# =========================================================
# RUTAS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SEGURIDAD
# =========================================================

SECRET_KEY = 'django-insecure-u4pp=fbxptdt#zn2-uoq%&hfpl6v)ufd$qs640a#p56ggqejty'

DEBUG = True

ALLOWED_HOSTS = []


# =========================================================
# APLICACIONES
# =========================================================

INSTALLED_APPS = [

    # -----------------------------------------------------
    # Django
    # -----------------------------------------------------

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # -----------------------------------------------------
    # Django Sites
    # -----------------------------------------------------

    'django.contrib.sites',

    # -----------------------------------------------------
    # Extensiones
    # -----------------------------------------------------

    'django_extensions',
    'embed_video',

    # -----------------------------------------------------
    # Django Allauth
    # -----------------------------------------------------

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # -----------------------------------------------------
    # Aplicaciones del proyecto
    # -----------------------------------------------------

    'apps.alumnos',
    'apps.user',
    'apps.paneles',
    'apps.clases',
    'apps.cursos',
    'apps.tareas',
    'apps.docentes',
    'apps.asistencia',
]
# =========================================================
# DJANGO SITES
# =========================================================

SITE_ID = 2


# =========================================================
# DJANGO ALLAUTH
# =========================================================

# Permitir iniciar sesión directamente con Google
# sin mostrar una página intermedia.

SOCIALACCOUNT_LOGIN_ON_GET = True


# Permitir identificar usuarios mediante
# el correo electrónico de Google.

SOCIALACCOUNT_EMAIL_AUTHENTICATION = True


# Conectar automáticamente una cuenta de Google
# con un usuario existente que tenga el mismo correo.

SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True


# =========================================================
# ADAPTADOR PERSONALIZADO DE GOOGLE
# =========================================================

SOCIALACCOUNT_ADAPTER = (
    "apps.user.adapters.CustomSocialAccountAdapter"
)


# =========================================================
# REDIRECCIONES
# =========================================================

# Después de iniciar sesión correctamente.

LOGIN_REDIRECT_URL = "/redireccionar/"


# Después de cerrar sesión.

LOGOUT_REDIRECT_URL = "/"


# URL utilizada cuando una vista requiere
# que el usuario esté autenticado.

LOGIN_URL = "/login/"


# =========================================================
# CONFIGURACIÓN DE GOOGLE
# =========================================================

SOCIALACCOUNT_PROVIDERS = {

    "google": {

        "SCOPE": [

            "profile",

            "email",

        ],

        "AUTH_PARAMS": {

            "access_type": "online",

        },

    },

}


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # -----------------------------------------------------
    # Django Allauth
    # -----------------------------------------------------

    'allauth.account.middleware.AccountMiddleware',

]


# =========================================================
# URLS
# =========================================================

ROOT_URLCONF = 'config.urls'


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [

    {

        'BACKEND':
            'django.template.backends.django.DjangoTemplates',

        'DIRS': [

            BASE_DIR / 'templates'

        ],

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


# =========================================================
# WSGI
# =========================================================

WSGI_APPLICATION = 'config.wsgi.application'


# =========================================================
# BASE DE DATOS
# =========================================================

DATABASES = {

    'default': {

        'ENGINE':
            'django.db.backends.sqlite3',

        'NAME':
            BASE_DIR / 'db.sqlite3',

    }

}


# =========================================================
# CONFIGURACIÓN DE CORREO GMAIL
# =========================================================

# Django utilizará el servidor SMTP de Gmail
# para enviar correos reales.

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)


# Servidor SMTP de Gmail.

EMAIL_HOST = "smtp.gmail.com"


# Puerto SMTP para conexión TLS.

EMAIL_PORT = 587


# Activar conexión segura TLS.

EMAIL_USE_TLS = True


# Cuenta Gmail que utilizará Educatec
# para enviar los correos.

EMAIL_HOST_USER = (
    "yubenferneyvargascaro@gmail.com"
)


# =========================================================
# CONTRASEÑA DE APLICACIÓN DE GMAIL
# =========================================================

# IMPORTANTE:
#
# NO utilices la contraseña normal de Gmail.
#
# Debes generar una contraseña de aplicación
# desde la cuenta de Google.

EMAIL_HOST_PASSWORD = (
    "rdpoorqrogniqpjk"
)


# Dirección que aparecerá como remitente.

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# =========================================================
# VALIDACIÓN DE CONTRASEÑAS
# =========================================================

AUTH_PASSWORD_VALIDATORS = [

    {

        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',

    },

    {

        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',

    },

    {

        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',

    },

    {

        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',

    },

]


# =========================================================
# INTERNACIONALIZACIÓN
# =========================================================

LANGUAGE_CODE = 'es'


TIME_ZONE = 'UTC'


USE_I18N = True


USE_TZ = True


# =========================================================
# ARCHIVOS ESTÁTICOS
# =========================================================

STATIC_URL = 'static/'


STATICFILES_DIRS = [

    BASE_DIR / 'static',

]


# =========================================================
# ARCHIVOS MEDIA
# =========================================================

MEDIA_URL = '/media/'


MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================
# USUARIO PERSONALIZADO
# =========================================================

AUTH_USER_MODEL = 'user.Usuario'