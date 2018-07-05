from my_django.conf import settings
from my_django.conf.urls import patterns
from my_django.core.urlresolvers import LocaleRegexURLResolver

def i18n_patterns(prefix, *args):
    """
    Adds the language code prefix to every URL pattern within this
    function. This may only be used in the root URLconf, not in an included
    URLconf.

    """
    pattern_list = patterns(prefix, *args)
    if not settings.USE_I18N:
        return pattern_list
    return [LocaleRegexURLResolver(pattern_list)]


urlpatterns = patterns('',
    (r'^setlang/$', 'my_django.views.i18n.set_language'),
)
