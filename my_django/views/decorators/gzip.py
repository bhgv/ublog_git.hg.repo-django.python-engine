from my_django.utils.decorators import decorator_from_middleware
from my_django.middleware.gzip import GZipMiddleware

gzip_page = decorator_from_middleware(GZipMiddleware)
gzip_page.__doc__ = "Decorator for views that gzips pages if the client supports it."
