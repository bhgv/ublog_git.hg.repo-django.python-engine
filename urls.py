from my_django.conf.urls.defaults import *

from my_django.conf import settings

import sys


# Uncomment the next two lines to enable the admin:
from my_django.contrib import admin
admin.autodiscover()

#from my_django.urls import include, path


urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'my_django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('my_django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/(.*)', admin.site.root),
    (r'^admin/', include(admin.site.urls)),

    (r'^git/', include('my_klaus.urls', namespace='klaus')),
    (r'^hg/', include('django_hg.urls')),

    (r'^(.*/)*css/(?P<path>.*)$', 'my_django.views.static.serve',
        {'document_root': settings.CICERO_PATH_TO_CSS}),
#    (r'^' + settings.MEDIA_URL + r'/(?P<path>.*)$', 
    (r'^files/(?P<path>.*)$',
	'my_django.views.static.serve',
	{'document_root': settings.MEDIA_ROOT}),

    (r'^(.*/)*cauth/login/$', 'cicero.views.login'),
    (r'^(.*/)*cauth/logout/$', 'cicero.views.logout'),
    (r'^(.*/)*cauth/newuser/$', 'cicero.views.newuser'),

    (r'^', include('cicero.urls')),
)
