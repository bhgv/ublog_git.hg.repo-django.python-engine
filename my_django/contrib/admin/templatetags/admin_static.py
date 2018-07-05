from my_django.conf import settings
from my_django.template import Library

register = Library()

if 'my_django.contrib.staticfiles' in settings.INSTALLED_APPS:
    from my_django.contrib.staticfiles.templatetags.staticfiles import static
else:
    from my_django.templatetags.static import static

static = register.simple_tag(static)
