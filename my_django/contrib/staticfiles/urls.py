from my_django.conf import settings
from my_django.conf.urls.static import static

urlpatterns = []

def staticfiles_urlpatterns(prefix=None):
    """
    Helper function to return a URL pattern for serving static files.
    """
    if prefix is None:
        prefix = settings.STATIC_URL
    return static(prefix, view='my_django.contrib.staticfiles.views.serve')

# Only append if urlpatterns are empty
if settings.DEBUG and not urlpatterns:
    urlpatterns += staticfiles_urlpatterns()
