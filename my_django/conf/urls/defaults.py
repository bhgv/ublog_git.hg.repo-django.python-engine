import warnings
warnings.warn("my_django.conf.urls.defaults is deprecated; use my_django.conf.urls instead",
              PendingDeprecationWarning)

from my_django.conf.urls import (handler403, handler404, handler500,
        include, patterns, url)
