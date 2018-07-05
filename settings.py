# Django settings for f project.
import os.path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

CICERO_PATH_TO_CSS = BASE_DIR + "/css/"

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(PROJECT_ROOT)


SECRET_KEY = 'm1e4^p+fl!bf9$oq4!$y@kpvc7u35bz!$8r4_yes)o3qt6ies9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG


ALLOWED_HOSTS = [u'bhgv.pythonanywhere.com']


ADMINS = (
#     ('basmp', 'your_email@domain.com'),
)


MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = PROJECT_ROOT + '/db/cicero.db'
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

DATABASES = {
    'default': {
        'ENGINE': 'my_django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': PROJECT_ROOT + '/db/cicero.db',
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
     }
}

#LOG_ROOT = os.path.join(PROJECT_ROOT, '/db')
LOG_ROOT = PROJECT_ROOT + '/db'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'utf-8'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + "/files/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'files/'
#MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'files/'

STATIC_ROOT = PROJECT_ROOT + '/static'
STATIC_URL = '/static/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    'my_django.template.loaders.filesystem.load_template_source',
    'my_django.template.loaders.filesystem.Loader',
#    'my_django.template.loaders.app_directories.load_template_source',
    'my_django.template.loaders.app_directories.Loader',
#     'my_django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'my_django.middleware.common.CommonMiddleware',
    'my_django.contrib.sessions.middleware.SessionMiddleware',
    'my_django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'
#ROOT_URLCONF = 'bhgv.urls'


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/my_django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)



# VVVV django hg
# /PROJECT/APP/settings.py
# django_hg settings
DJANGO_HG_REPOSITORIES_DIR = {
  "public": PROJECT_ROOT + "/repo/hg/pub/",
  "private": PROJECT_ROOT + "/repo/hg/priv/"
}
DJANGO_HG_PAGER_ITEMS = 7
# one of pygment styles : autumn, borland, bw, colorful, default, emacs,
# friendly, fruity, manni, murphy, native, pastie, perldoc, tango, trac, vim,
# vs
DJANGO_HG_PYGMENT_STYLE = 'tango'
# The maximum of search results returned when performing a search in a repository
DJANGO_HG_MAX_SEARCH_RESULTS = 100

# templates dir
TEMPLATE_DIRS = (
    os.path.dirname(__file__) + '/django_hg/templates',
    os.path.dirname(__file__) + '/cicero/templates/cicero',
    os.path.dirname(__file__) + '/my_klaus/templates',
)

# if not already done, add the DJANGO.CORE.CONTEXT_PROCESSORS.REQUEST and
# the DJANGO.CORE.CONTEXT_PROCESSORS.MEDIA to settings
TEMPLATE_CONTEXT_PROCESSORS = (
    'my_django.core.context_processors.request',
    'my_django.core.context_processors.media',
    'my_django.core.context_processors.static',
#    'my_django.core.context_processors.auth',
    'my_django.contrib.auth.context_processors.auth',
)
# ^^^^ django hg


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'my_django.contrib.staticfiles.finders.FileSystemFinder',
    'my_django.contrib.staticfiles.finders.AppDirectoriesFinder',
)





INSTALLED_APPS = (
    'my_django.contrib.auth',
    'my_django.contrib.contenttypes',
    'my_django.contrib.sessions',
    'my_django.contrib.sites',
    'my_django.contrib.admin',

    'my_django.contrib.staticfiles',

    'django_hg',

    'cicero',

    'my_klaus',
)



from gitrepo_path import REPO_HOME



#MIDDLEWARE_CLASSES = (
#    'my_django.middleware.security.SecurityMiddleware',
#    'my_django.contrib.sessions.middleware.SessionMiddleware',
#    'my_django.middleware.common.CommonMiddleware',
#    'my_django.middleware.csrf.CsrfViewMiddleware',
#    'my_django.contrib.auth.middleware.AuthenticationMiddleware',
#    'my_django.contrib.messages.middleware.MessageMiddleware',
#    'my_django.middleware.clickjacking.XFrameOptionsMiddleware',
#
##    'my_django.middleware.csrf.CsrfViewMiddleware',
#)



from cicero.settings import *

AUTHENTICATION_BACKENDS = (
    'my_django.contrib.auth.backends.ModelBackend',
)



#TEMPLATES = [
#    {
#        'BACKEND': 'my_django.template.backends.django.DjangoTemplates',
#        'DIRS': [],
#        'APP_DIRS': True,
#        'OPTIONS': {
#            'context_processors': [
#                'my_django.template.context_processors.debug',
#                'my_django.template.context_processors.request',
#                'my_django.contrib.auth.context_processors.auth',
#                'my_django.contrib.messages.context_processors.messages',
#            ],
#        },
#    },
#]

WSGI_APPLICATION = 'wsgi.application'
