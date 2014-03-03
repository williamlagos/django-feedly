#
# This file is part of Efforia Open Source Initiative.
#
# Copyright (C) 2011-2014 William Oliveira de Lagos <william@efforia.com.br>
#
# Efforia is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Efforia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Efforia. If not, see <http://www.gnu.org/licenses/>.
#

import sys,os

sys.path.append(os.path.abspath('..'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'America/Sao_Paulo'
LANGUAGE_CODE = 'pt-br'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_DATE = ("Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez")

MEDIA_ROOT = ''
MEDIA_URL = ''

SECRET_KEY = 'x5dvfbk$u-(07^f1229p*_%rcuc+nka45j6awo==*jkyjiucql'

STATIC_ROOT = os.path.abspath('static')
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.abspath('public')]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
    }
}

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'demo.urls'
WSGI_APPLICATION = 'demo.wsgi.application'
TEMPLATE_DIRS = [
    os.path.abspath('templates/control'),
    os.path.abspath('templates/context'),
    os.path.abspath('templates'),
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'pure_pagination',
    'feedly',
    'demo'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_efforiaid'
SOCIAL_AUTH_UID_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 16
SOCIAL_AUTH_NONCE_SERVER_URL_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_SERVER_URL_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 16

LOGIN_URL          = '/demo/participate'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/'

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
ANONYMOUS_USER_ID = -1
AUTH_PROFILE_MODULE = 'demo.Profile'

EFFORIA_APPS = ['demo']
EFFORIA_ACTIONS = {'demo':[]}
EFFORIA_OBJS = {'demo':[]}
EFFORIA_NAMES = {}
EFFORIA_TOKENS = {}
EFFORIA_URL = ''

PAYPAL_RECEIVER_EMAIL = 'efforiaca@gmail.com'
PAYPAL_NOTIFY_URL = ''
PAYPAL_RETURN_URL = ''
PAYPAL_CANCEL_RETURN = ''
PAGSEGURO_EMAIL_COBRANCA = 'efforiaca@gmail.com'
PAGSEGURO_TOKEN = ''