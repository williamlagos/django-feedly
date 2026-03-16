"""
Django test settings for django-feedly.
"""

SECRET_KEY = 'test-secret-key-for-django-feedly-do-not-use-in-production'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'feedly',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

ROOT_URLCONF = 'feedly.urls'

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
