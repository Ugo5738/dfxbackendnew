from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]


# ================================ DATABASES =======================================
# DATABASES = {"default": dj_database_url.config(default='sqlite:///db.sqlite3', conn_max_age=600)}
# # Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {"default": dj_database_url.parse(config("DATABASE_URL"))}
# ================================ DATABASES =======================================


# ================================ STORAGES =======================================
# ==> STATIC FILE UPLOADS
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ==> MEDIA FILE UPLOADS
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
# ================================ STORAGES =======================================


# ================================ EMAIL =======================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.office365.com'  # 'smtp.outlook.office365.com'
EMAIL_PORT = 587  # 465  # TLS port
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True
EMAIL_HOST_USER = config("EMAIL")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("EMAIL")
# ================================ EMAIL =======================================


# ================================ REDIS =======================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
# ================================ REDIS =======================================


# ================================ PAYSTACK =======================================
PAYSTACK_PUBLIC_KEY=config("PAYSTACK_TEST_PUBLIC_KEY")
PAYSTACK_SECRET_KEY=config("PAYSTACK_TEST_SECRET_KEY")
# ================================ PAYSTACK =======================================
