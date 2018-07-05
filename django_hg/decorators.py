# coding=utf-8
# This decorator is based on django snippet 243:
# http://www.djangosnippets.org/snippets/243/

import base64

from my_django.http import HttpResponse, HttpResponseRedirect
from my_django.contrib.auth import authenticate, login
from my_django.shortcuts import get_object_or_404
from my_django.conf import settings as global_settings
from models import HgRepository, HgRepositoryManager

def __get_repo(request, name):
    """
    this private function get the repository object from the database and
    returns the context view of the repository
    """
    return get_object_or_404(HgRepository, name=name) #HgRepository.objects.get(name=name)

def HttpResponseUnauthorized(realm):
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response

##############################################################################
def view_or_basicauth(view, request, test_func, realm = "", *args, **kwargs):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """
    print request.user
    if test_func(request.user):
        # Already logged in, just return the view.
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    if 'HTTP_AUTHORIZATION' in request.META:
        print "HTTP_AUTHORIZATION : %s\n%s" % (request.META['HTTP_AUTHORIZATION'], request.META['HTTP_AUTHORIZATION'].split())
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                print ("uname, passwd, is_active = %s, %s, %s" % 
                      (uname, passwd, user.is_active, #repo.user_can_write(user)
                      ))
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        #return view(request, *args, **kwargs)
                        # check that the user is allowed to command to the
                        # given repository
                        repo = __get_repo(request, kwargs['name'])
                        if repo:
                        #    if request.GET.get('cmd') :
                                #print 'on doit etre la'
                            if repo.user_can_write(request.user):
                                return view(request, *args, **kwargs)
                            else:
                                return HttpResponseUnauthorized(realm)
    # Test if an authentication is needed:
    # if the request is an Hg command and the related repo is private
    # or if the request is an Hg push and the related repo is public (ie
    # with anonymous_access = True), we send an 401 to ask users to authenticate,
    # otherwise, just return the view
    # It seems that Hg doesn't always send HTTP_AUTHORIZATION even after an
    # authentication has been set, so we can't check every request of a command
    # to a private repo: we just check the first one
    repo = __get_repo(request, kwargs['name'])
    if (request.GET.get('cmd') and request.GET.get('cmd') == 'unbundle' and repo \
        and repo.anonymous_access == True) \
        or (request.GET.get('cmd') and request.GET.get('cmd') == 'between' and repo \
        and repo.anonymous_access == False):
        # in HgRepository.cmds
        return HttpResponseUnauthorized(realm)

    return view(request, *args, **kwargs)

#############################################################################
#
def logged_in_or_basicauth(realm = ""):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    Use is simple:

    @logged_in_or_basicauth
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """

    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated() and ('%s' % (u,)) != 'AnonymousUser',
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator

#############################################################################
#
def has_perm_or_basicauth(perm, realm = ""):
    """
    This is similar to the above decorator 'logged_in_or_basicauth'
    except that it requires the logged in user to have a specific
    permission.

    Use:

    @logged_in_or_basicauth('asforums.view_forumcollection')
    def your_view:
        ...

    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.has_perm(perm),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator
