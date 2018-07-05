from my_django.conf.urls import patterns

urlpatterns = patterns('my_django.views',
    (r'^(?P<content_type_id>\d+)/(?P<object_id>.*)/$', 'defaults.shortcut'),
)
