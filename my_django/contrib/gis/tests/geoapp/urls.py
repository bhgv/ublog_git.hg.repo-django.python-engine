from __future__ import absolute_import

from my_django.conf.urls import patterns

from .feeds import feed_dict
from .sitemaps import sitemaps


urlpatterns = patterns('',
    (r'^feeds/(?P<url>.*)/$', 'my_django.contrib.gis.views.feed', {'feed_dict': feed_dict}),
)

urlpatterns += patterns('my_django.contrib.gis.sitemaps.views',
    (r'^sitemap.xml$', 'index', {'sitemaps' : sitemaps}),
    (r'^sitemaps/(?P<section>\w+)\.xml$', 'sitemap', {'sitemaps' : sitemaps}),
    (r'^sitemaps/kml/(?P<label>\w+)/(?P<model>\w+)/(?P<field_name>\w+)\.kml$', 'kml'),
    (r'^sitemaps/kml/(?P<label>\w+)/(?P<model>\w+)/(?P<field_name>\w+)\.kmz$', 'kmz'),
)
