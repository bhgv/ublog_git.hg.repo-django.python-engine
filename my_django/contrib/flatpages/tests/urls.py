from my_django.conf.urls import patterns, include

# special urls for flatpage test cases
urlpatterns = patterns('',
    (r'^flatpage_root', include('my_django.contrib.flatpages.urls')),
    (r'^accounts/', include('my_django.contrib.auth.urls')),
)

