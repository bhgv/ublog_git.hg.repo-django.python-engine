import os.path
from my_django.conf.urls.defaults import *
from my_django.conf import settings

urlpatterns = patterns('django_hg.views',
    url(r'^$', 'list', {'tab': 'dashboard'},name='hg-list'),
    url(r'all/$', 'list', {'tab': 'all' }, name='hg-list-all'),
    url(r'^(?P<name>(\w|\d|\.|\-|\_)+)/(?P<action>(\w|\d)+)/(?P<rev>(\w|\d)+)/(?P<path>(\w|\d|\.|\-|\_|\/)+)$',
        'repo',
        name="hg-repo-action-rev-path"),
    url(r'^(?P<name>(\w|\d|\.|\-|\_)+)/(?P<action>(\w|\d)+)/(?P<rev>(\w|\d)+)/$',
        'repo',
        name="hg-repo-action-rev"),
    url(r'^(?P<name>(\w|\d|\.|\-|\_)+)/(?P<action>(\w|\d)+)/$',
        'repo',
        {'rev': 'tip'},
        name="hg-repo-action"),
    url(r'^(?P<name>(\w|\d|\.|\-|\_)+)/$',
        'repo',
        {'action': 'overview',
         'rev': 'tip' },
        name="hg-repo"),
    )
