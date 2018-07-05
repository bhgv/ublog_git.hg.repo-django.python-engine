from my_django.conf.urls import patterns

urlpatterns = patterns('my_django.contrib.flatpages.views',
    (r'^(?P<url>.*)$', 'flatpage'),
)
