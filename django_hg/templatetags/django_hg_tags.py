# coding=utf-8
from datetime import datetime
import time
#import pytz
#from pytz import timezone
from math import ceil

from my_django.core.urlresolvers import reverse
from my_django.conf import settings as global_settings
from my_django.template import Library


register = Library()

@register.simple_tag
def active(request, pattern):
    """
    Return "active" if the given pattern is found in current request path
    >>> class Request():
    ...     def __init__(self, path):
    ...         self.path = path
    >>> active(Request('foo/bar'), 'foo/bar')
    'active'
    >>> active(Request('foo/bar/baz/foo/bar/'), 'foo/bar/baz/foo/')
    'active'
    >>> active(Request('foo/bar'), 'baz')
    ''
    
    """
    # for deep paths we need to take only the first parts of the request path
    if len(pattern.split('/')) > 4 :
        if request.path.startswith(pattern):
            return 'active'
    else:
        if request.path == pattern:
            return 'active'
    return ''


@register.inclusion_tag('django_hg/filedisplay.html', takes_context=True)
def filedisplay(context):
    """
    Display a file at a given revision.
    According to the mimetype, the file may be displayed as source, colored
    thanks to Pygments, or, for pictures and PDF, directly in the browser
    """
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_for_mimetype, guess_lexer_for_filename
    import mimetypes

    if 'raw' in context['request'].GET:
        mimetype = ('text/plain', None)
    else:
        mimetype = mimetypes.guess_type(context['file'])

    if mimetype != ('text/plain', None) :
        lexer = None
        if mimetype[0] is not None:
            try:
                lexer = get_lexer_for_mimetype(mimetype)
            except:
                lexer = None
        if lexer is None:
            try:
                lexer = guess_lexer_for_filename(context['file'],
                                                 context['fctx'].data())
            except:
                lexer = None
    else:
        # a lexer can't be guess from plain text mimetype.
        # we force the file to be view as text
        try:
            lexer = guess_lexer_for_filename(context['file'] + '.txt',
                                             context['fctx'].data())
        except:
            lexer = None
    
    if lexer :
        formatter = HtmlFormatter(linenos=True, cssclass="source")
        content = highlight(context['fctx'].data(), lexer, formatter)
    else:
        lexer = None
        if mimetype[0] == 'image/png' or mimetype[0] == 'image/jpeg' or mimetype[0] == 'image/gif':
            content = 'image'
        elif mimetype[0] == 'application/pdf':
            content = 'pdf'
        else:
            content = None

    return {
        'content': content,
        'lexer': lexer,
        'mimetype': mimetype,
        'file': context['file'],
        'size': context['fctx'].size(),
        'name': context['repo'],
        'rev': context['rev']
    }

#@register.filter(name='format_hg_date')
#def format_hg_date(value):
#    """
#    Build a date from the timestamp returned by hg.
#
#    As for now, the tz is not handled
#
#    >>> format_hg_date([1234567890, -7200])
#    '2009-02-13 23:31:30+01:00'
#    """
#    django_tz = pytz.timezone(global_settings.TIME_ZONE)
#    #print datetime.utcfromtimestamp(time.time())print datetime.fromtimestamp(time.time())
#    #print datetime.utcfromtimestamp(time.time())
#    #print datetime.fromtimestamp(time.time())
#    #print datetime.utcfromtimestamp(time.time())
#    #print django_tz.localize(datetime.utcfromtimestamp(time.time())).astimezone(django_tz)
#
#    utc = datetime.utcfromtimestamp(value[0])
#    #import locale
#    #locale.setlocale(locale.LC_TIME, "sv_SE")
#
#    return '%(datetime)s' % { 'datetime': django_tz.localize(utc, is_dst=True) }

@register.filter(name='format_hg_user')
def format_hg_user(value):
    """
    Return the user name from the Mercurial committer. Especially, try to hide
    the e-mail address if present
    >>> format_hg_user('Foo')
    'Foo'

    >>> format_hg_user('Foo bar')
    'Foo bar'

    >>> format_hg_user('Foo bar <foo@bar.com>')
    'Foo bar'

    >>> format_hg_user('Foo bar <foo@bar.com>, Baz <baz@bar.com>')
    'Foo bar, Baz'

    >>> format_hg_user('Foo, Bar, Baz')
    'Foo, Bar, Baz'
    """
    if value.find(',')> -1:
        elts = value.split(', ')
    else:
        elts = [value]
    names = []
    for elt in elts:
        parts = elt.split(' ')
        name = []
        for part in parts:
            if not part.startswith('<'):
                name.append(part)
        names.append(' '.join(name))

    return ', '.join(names)


@register.simple_tag
def hg_diff_class(line):
    if line.startswith('+'):
        return "added"
    elif line.startswith('-'):
        return "removed"
    else:
        return 'unchanged'
    
@register.inclusion_tag('django_hg/pagination.html', takes_context=True)
def paginate(context):
    """
    Based on Eric Florenzano paginator
    http://eflorenzano.com/blog/post/first-two-django-screencasts/#using-django-pagination
    Renders the ``hg/pagination.html`` template, resulting in a
    Digg-like display of the available pages, given the current page. If there
    are too many pages to be displayed before and after the current page, then
    ellipses will be used to indicate the undisplayed gap between page numbers.

    Requires one argument, ``context``, which should be a dictionary-like data
    structure and must contain the following keys:
    ``page``
        the current page
    ``items_per_page``
        the max number of items per page
    ``max``
        the greatest item in the list

    >>> paginate({'name': 'repo_test', 'page': 1,'items_per_page': 20,'max': 10 })
    {'max': 10, 'previous': 0, 'getvars': '', 'pages': [], 'pages_count': 1, 'is_paginated': False, 'page': 1, 'next': 2}

    >>> paginate({'name': 'repo_test', 'page': 1,'items_per_page': 20,'max': 30 })
    {'max': 30, 'previous': 0, 'getvars': '', 'pages': [1, 2], 'pages_count': 2, 'is_paginated': True, 'page': 1, 'next': 2}

    >>> paginate({'name': 'repo_test', 'page': 1,'items_per_page': 20,'max': 300 })
    {'max': 300, 'previous': 0, 'getvars': '', 'pages': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'ellipsis', 14, 15], 'pages_count': 15, 'is_paginated': True, 'page': 1, 'next': 2}

    >>> paginate({'name': 'repo_test', 'page': 6,'items_per_page': 20,'max': 300 })
    {'max': 300, 'previous': 5, 'getvars': '', 'pages': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 'ellipsis', 14, 15], 'pages_count': 15, 'is_paginated': True, 'page': 6, 'next': 7}

    >>> paginate({'name': 'repo_test', 'page': 9,'items_per_page': 20,'max': 300 })
    {'max': 300, 'previous': 8, 'getvars': '', 'pages': [1, 2, 'ellipsis', 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 'pages_count': 15, 'is_paginated': True, 'page': 9, 'next': 10}

    >>> paginate({'name': 'repo_test', 'page': 15,'items_per_page': 20,'max': 300 })
    {'max': 300, 'previous': 14, 'getvars': '', 'pages': [1, 2, 'ellipsis', 10, 11, 12, 13, 14, 15], 'pages_count': 15, 'is_paginated': True, 'page': 15, 'next': 16}

    """
    page = context['page']
    items_per_page = context['items_per_page']
    max = context['max']

    # we need to convert max and items_per_page to float, otherwise Python
    # performs an euclidian division (ie 3/2 = 1)
    pages_count = int(ceil(float(max)/float(items_per_page)))
    is_paginated = False
    if pages_count > 1:
        is_paginated = True
    pages = []

    if pages_count > 1 and pages_count <= 10 :
        # there will be only one block of pages
        pages = [i for i in range(1, pages_count+1)]
    elif pages_count > 1 and pages_count > 10 :
        # there will be at least 2 blocks, maybe 3
        if page-5 <= 0:
            start = 1
            if page + 6 > 10:
                end = page + 6
            else:
                end = 11
        else:
            start = page-5
            end = page + 6
        if end > pages_count:
            end = pages_count+1
        pages = [i for i in range(start, end)]

        # add ellipsis if needed
        if (pages[0] != 1 and pages[0] != 2):
            pages.insert(0, 'ellipsis')
            pages.insert(0, 2)
            pages.insert(0, 1)
        if (pages[0] == 2):
            pages.insert(0, 1)
        if (pages[len(pages)-1] != pages_count
            and pages[len(pages)-1] != pages_count-1
            and pages[len(pages)-1] != pages_count-2):
            pages.insert(len(pages), 'ellipsis')
            pages.insert(len(pages), pages_count-1)
            pages.insert(len(pages), pages_count)
        if pages[len(pages)-1] == pages_count-2:
            pages.insert(len(pages), pages_count-1)
        if pages[len(pages)-1] == pages_count-1:
            pages.insert(len(pages), pages_count)
    
    getvars = ''
    if 'request' in context:
        getvars = context['request'].GET.copy()
        if 'page' in getvars:
            del getvars['page']
        if len(getvars.keys()) > 0:
            getvars = "&%s" % getvars.urlencode()
        else:
            getvars = ''

    return {
            'is_paginated': is_paginated,
            'getvars': getvars,
            'max': max,
            'next': page+1,
            'page': page,
            'pages_count': pages_count,
            'pages': pages,
            'previous': page-1,
        } #pagination

@register.inclusion_tag('django_hg/path.html', takes_context=True)
def path(context):
    """
    Build a path for the navigation into the repository.

    >>> class Foo():
    ...     def __init__(self, name):
    ...         self.name = name
    ...
    ...     def __str__(self):
    ...         return self.name
    >>> path({'repo': Foo('foo'), 'rev': 'bar'})
    {'path': [{'url': '/hg/foo/browse/bar/', 'name': 'foo'}]}

    >>> path({'repo': Foo('foo'), 'rev': 'bar', 'path': 'baz/'})
    {'path': [{'url': '/hg/foo/browse/bar/', 'name': 'foo'}, {'url': '/hg/foo/browse/bar/baz/', 'name': 'baz'}]}

    >>> path({'repo': Foo('foo'), 'rev': 'bar', 'path': 'baz/foo/'})
    {'path': [{'url': '/hg/foo/browse/bar/', 'name': 'foo'}, {'url': '/hg/foo/browse/bar/baz/', 'name': 'baz'}, {'url': '/hg/foo/browse/bar/baz/foo/', 'name': 'foo'}]}
    """

    name = context['repo'].name
    rev = context['rev']
    try:
        path = context['path']
    except:
        path = ''
    
    if path != '' :
        elements = path.split('/')
    else:
        elements = []
    breadcrumb_path = []
    count = len(elements)
    for i in range(count):
        if elements[i] != '':
            previous = '/'.join([elements[elt] for elt in xrange(i+1)])
            if i != count-1:
                if previous == '':
                    # we browse the root
                    url = reverse('hg-repo-action-rev',
                                  kwargs={'action': 'browse', 'name': name, 'rev': rev})
                else:
                    url = reverse('hg-repo-action-rev-path',
                                  kwargs={'action': 'browse', 'name': name, 'rev': rev, 'path': previous + '/'})
            else:
                url = None
            breadcrumb_path.append({'name': elements[i], 'url': url})
    url = reverse('hg-repo-action-rev', kwargs={'action': 'browse', 'name': name, 'rev': rev})
    breadcrumb_path.insert(0, {'name': name, 'url': url})

    return {'path': breadcrumb_path}

@register.filter
def strip_path(value):
    """
    A pythonic version of PHP basename
    >>> strip_path('foo')
    'foo'

    >>> strip_path('foo/bar')
    'bar'

    >>> strip_path('foo/bar/')
    'bar'
    """
    if value.rfind('/') == len(value)-1:
        value = value[:value.rfind('/')]

    return value[value.rfind('/')+1:]


if __name__ == "__main__":
    import os.path, sys, doctest
    try:
        from my_django.core.management import setup_environ
    except:
        print "Unable to import setup_environ"
        sys.exit(1)
    # define PROJECT_PATH to a django project that use
    PROJECT_PATH = os.path.abspath('../../../../Sites/chaptrz/projects/core/')
    sys.path.append(PROJECT_PATH)
    try:
        import settings
    except ImportError:
        print "Unable to import settings. You need to define PROJECT_PATH to a"
        + "django project that use django_hg"
        sys.exit(1)
    setup_environ(settings)
    try:
        from my_django.conf.urls.defaults import *
    except:
        print "Unable to import urlconf"
        sys.exit(1)
    try:
        from django_hg.urls import urlpatterns
    except ImportError:
        print "Unable to import urlspatterns."
        sys.exit(1)

    doctest.testmod()
