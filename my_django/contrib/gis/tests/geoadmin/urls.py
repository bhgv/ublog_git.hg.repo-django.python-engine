from my_django.conf.urls import patterns, include
from my_django.contrib import admin

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)
