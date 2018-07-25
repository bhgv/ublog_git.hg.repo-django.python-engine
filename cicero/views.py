# -*- coding:utf-8 -*-
from my_django.views.generic.list_detail import object_list
from my_django.views.decorators.http import require_POST
#, condition
from my_django.views.decorators.cache import never_cache
from my_django.shortcuts import get_object_or_404, render_to_response
from my_django.http import HttpResponseNotAllowed, HttpResponseNotModified, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, Http404
from my_django.core.urlresolvers import reverse
from my_django.core.paginator import Paginator, InvalidPage
from my_django.utils import simplejson
from my_django.conf import settings

from my_django.contrib.auth.forms import AuthenticationForm

from cicero.models import Forum, Topic, Article, Profile
from cicero import forms
from cicero.context import default
from cicero import caching
#from cicero import antispam
from cicero.utils import absolute_url

from datetime import datetime


from calendar import timegm
from datetime import timedelta
from email.Utils import formatdate







#
# from django.utils.http 
#
import re

ETAG_MATCH = re.compile(r'(?:W/)?"((?:\\.|[^"])*)"')

def parse_etags(etag_str):
    """
    Parses a string with one or several etags passed in If-None-Match and
    If-Match headers by the rules in RFC 2616. Returns a list of etags
    without surrounding double quotes (") and unescaped from \<CHAR>.
    """
    etags = ETAG_MATCH.findall(etag_str)
    if not etags:
        # etag_str has wrong format, treat it as an opaque string then
        return [etag_str]
    etags = [e.decode('string_escape') for e in etags]
    return etags


def quote_etag(etag):
    """
    Wraps a string in double quotes escaping contents as necesary.
    """
    return '"%s"' % etag.replace('\\', '\\\\').replace('"', '\\"')

#
# from django.views.decorators.http
#
def condition(etag_func=None, last_modified_func=None):
    """
    Decorator to support conditional retrieval (or change) for a view
    function.

    The parameters are callables to compute the ETag and last modified time for
    the requested resource, respectively. The callables are passed the same
    parameters as the view itself. The Etag function should return a string (or
    None if the resource doesn't exist), whilst the last_modified function
    should return a datetime object (or None if the resource doesn't exist).

    If both parameters are provided, all the preconditions must be met before
    the view is processed.

    This decorator will either pass control to the wrapped view function or
    return an HTTP 304 response (unmodified) or 412 response (preconditions
    failed), depending upon the request method.

    Any behavior marked as "undefined" in the HTTP spec (e.g. If-none-match
    plus If-modified-since headers) will result in the view function being
    called.
    """
    def decorator(func):
        def inner(request, *args, **kwargs):
            # Get HTTP request headers
            if_modified_since = request.META.get("HTTP_IF_MODIFIED_SINCE")
            if_none_match = request.META.get("HTTP_IF_NONE_MATCH")
            if_match = request.META.get("HTTP_IF_MATCH")
            if if_none_match or if_match:
                # There can be more than one ETag in the request, so we
                # consider the list of values.
                try:
                    etags = parse_etags(if_none_match or if_match)
                except ValueError:
                    # In case of invalid etag ignore all ETag headers.
                    # Apparently Opera sends invalidly quoted headers at times
                    # (we should be returning a 400 response, but that's a
                    # little extreme) -- this is Django bug #10681.
                    if_none_match = None
                    if_match = None

            # Compute values (if any) for the requested resource.
            if etag_func:
                res_etag = etag_func(request, *args, **kwargs)
            else:
                res_etag = None
            if last_modified_func:
                dt = last_modified_func(request, *args, **kwargs)
                if dt:
                    res_last_modified = formatdate(timegm(dt.utctimetuple()))[:26] + 'GMT'
                else:
                    res_last_modified = None
            else:
                res_last_modified = None

            response = None
            if not ((if_match and (if_modified_since or if_none_match)) or
                    (if_match and if_none_match)):
                # We only get here if no undefined combinations of headers are
                # specified.
                if ((if_none_match and (res_etag in etags or
                        "*" in etags and res_etag)) and
                        (not if_modified_since or
                            res_last_modified == if_modified_since)):
                    if request.method in ("GET", "HEAD"):
                        response = HttpResponseNotModified()
                    else:
                        response = HttpResponse(status=412)
                elif if_match and ((not res_etag and "*" in etags) or
                        (res_etag and res_etag not in etags)):
                    response = HttpResponse(status=412)
                elif (not if_none_match and if_modified_since and
                        request.method == "GET" and
                        res_last_modified == if_modified_since):
                    response = HttpResponseNotModified()

            if response is None:
                response = func(request, *args, **kwargs)

            # Set relevant headers on the response if they don't already exist.
            if res_last_modified and not response.has_header('Last-Modified'):
                response['Last-Modified'] = res_last_modified
            if res_etag and not response.has_header('ETag'):
                response['ETag'] = quote_etag(res_etag)

            return response

        return inner
    return decorator



import sys
import os


def render_to_response(request, template_name, context_dict, **kwargs):
    from cicero.context import default
    from my_django.template import RequestContext
    from my_django.shortcuts import render_to_response as _render_to_response
    #if not kwargs.has_key('extra_context'):
    #    kwargs['extra_context'] = {}
    #kwargs['extra_context']['groups'] = _get_left_side_cont()
    context_dict['groups'] = _get_left_side_cont()
    context = RequestContext(request, context_dict, [default])
    return _render_to_response(template_name, context_instance=context, **kwargs)

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        defaults = {
          'content_type': 'application/json',
        }
        defaults.update(kwargs)
        super(JSONResponse, self).__init__(simplejson.dumps(data), defaults)

def post_redirect(request):
    return request.POST.get('redirect', request.META.get('HTTP_REFERER', '/'))

def login_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponse("403")
            #return HttpResponseRedirect(reverse('scipio_login') + '?redirect=' + request.path)
        return func(request, *args, **kwargs)
    return wrapper

def _publish_article(slug, article):
    article.set_spam_status('clean')
    from my_django.db import transaction
    if transaction.is_managed():
        transaction.commit()
    article.ping_external_links()
    caching.invalidate_by_article(slug, article.topic_id)

def _process_new_article(request, article, is_new_topic, check_login):
    #spam_status = antispam.conveyor.validate(request, article=article)

    # Detected spam is deleted independant on check_login because
    # an OpenID server may not return from a check and the spam will hang forever
    #if spam_status == 'spam':
    #    forum = article.topic.forum
    #    article.delete()
    #    return render_to_response(request, 'cicero/spam.html', {
    #        'forum': forum,
    #        'text': article.text,
    #        'admins': [e for n, e in settings.ADMINS],
    #    })
    
    spam_status = 'clean'

    if check_login and not request.user.is_authenticated():
        form = AuthenticationForm(request, {'openid_identity': request.POST['name']})
        #form = AuthForm(request.session, {'openid_identity': request.POST['name']})
        if form.is_valid():
            article.set_spam_status(spam_status)
            url = form.auth_redirect(post_redirect(request), data={'op': 'login', 'acquire': str(article.pk)})
            return HttpResponseRedirect(url)
    if spam_status == 'clean':
        slug = article.topic.forum.slug
        _publish_article(slug, article)
        url = reverse(topic, args=[slug, article.topic_id])
        if not is_new_topic:
            url += '?page=last'
        url += '#%s' % article.id
        return HttpResponseRedirect(url)
    # Любой не-clean и не-spam статус -- разного рода подозрения
    article.set_spam_status(spam_status)
    return render_to_response(request, 'cicero/spam_suspect.html', {
        'article': article,
    })

generic_info = {
    'paginate_by': settings.CICERO_PAGINATE_BY,
    'allow_empty': True,
    'context_processors': [default],
}

def get_left_side_cont_a():
    return _get_left_side_cont().a

def get_left_side_cont_f():
    return _get_left_side_cont().f

def _get_left_side_cont():
    grps_a = {}
    grps_f = {}
    for fm in Forum.objects.all():
        #if not grps.has_key(fm.group):
        #    grps[fm.group] = []
        
        if not grps_f.has_key(fm.group):
            grp = []
            for fmb in Forum.objects.filter(group = fm.group, is_forum = True):
                grp.append({'name': fmb.name, 'slug': fmb.slug, 'is_forum': fmb.is_forum})
            if len(grp) > 0:
                grps_f[fm.group] = grp
                
#        f = open(r"http://basmphg.heliohost.org/f/whois/", "r")
#        if f:
#            f.read()
#            f.close()
        
        if not grps_a.has_key(fm.group):
            grp = []
            for fmb in Forum.objects.filter(group = fm.group, is_forum = False):
                grp.append({'name': fmb.name, 'slug': fmb.slug, 'is_forum': fmb.is_forum})
            if len(grp) > 0:
                grps_a[fm.group] = grp
    
    groups = {'a':[], 'f':[]}
    for k in grps_a.keys():
        groups['a'].append({'group': k, 'cont': grps_a[k]})
    for k in grps_f.keys():
        groups['f'].append({'group': k, 'cont': grps_f[k]})
    
    return groups


def _get_summary_cont(request):
    f = open(settings.LOG_ROOT + "/log.txt", "a")
    if f:
        f.write("%s ::\n\t%s ::\n\t%s ::\n\t%s\n\n" % 
            (datetime.now(), request.META['REMOTE_ADDR'], request.META['HTTP_USER_AGENT'], request.user)
        )
        f.close()

    if not request.user.is_authenticated():
        return None
    
    profile = request.user.cicero_profile
  
    summary = {
            'posts': profile.max_posts - profile.today_posts,
            'edits': profile.max_edits - profile.today_edits,
            'carmas': profile.max_change_carmas - profile.today_change_carmas,
            'user_carma': profile.carma,
    }
    
    return summary

@never_cache
@condition(caching.user_etag, caching.latest_change)
def logout(request, *args, **kwargs):
    from my_django.contrib.auth import logout
    logout(request)
    try:
        del request.session['member_id']
    except KeyError:
        pass
    #return HttpResponse("You're logged out.")
#    url = '%s#%s' % (reverse(topic, args=(article.topic.forum.slug, article.topic.id)), article.id)
#    print url

#    return HttpResponseRedirect(request.META.get('HTTP_REFERER') or '../')
    return HttpResponseRedirect(post_redirect(request))

@never_cache
@condition(caching.user_etag, caching.latest_change)
def login(request, *args, **kwargs):
    #print "+++++++++++++++++++++++++++++++++++++++++++++++"
    #print request.POST
    #print "+0+++++++++++++++++++++++++++++++++++++++++++++"
    
    usernm = request.POST['openid_identity']
    passwd = request.POST['openid_password']

    if request.user.is_authenticated():
        usernm = request.user.username
        return HttpResponse("You already logged %s." % (usernm,))
    else:
        if request.method == 'POST': # If the form has been submitted...
            #form = LoginForm(request.POST) # A form bound to the POST data
            #if form.is_valid(): # All validation rules pass
            
            from my_django.contrib.auth import authenticate, login
            
            user = authenticate(username=usernm, password=passwd)
            if user is not None:
                if user.is_active:
                    # Redirect to a success page.
                    login(request, user)
                    #return HttpResponse(u'ok')
                    #return HttpResponseRedirect(reverse('scipio_login') + '?redirect=' + request.path)
                    #print post_redirect(request)
                    return HttpResponseRedirect(post_redirect(request))

                else:
                    # Return a 'disabled account' error message
                    error = u'account disabled'
                    return HttpResponse(error)
            else:
                # Return a 'disabled account' error message
                error = u'wrong logid'
                return HttpResponse(error)

        else:
            return HttpResponse("No found login data.")
    return HttpResponse("--???--")
    
    
@never_cache
@condition(caching.user_etag, caching.latest_change)
def newuser(request, *args, **kwargs):

    lst = Profile.objects.filter(
                        registered_date = datetime.now().date(),
                        registered_ip = request.META['REMOTE_ADDR'],
                              ).select_related()
    if len(lst) > 0:
        return HttpResponse("вы уже регистрировались сегодня")

    # If we submitted the form...
    if request.method == 'POST':
        from my_django.contrib.auth.models import User

        usernm = request.POST['openid_identity']
        passwd = request.POST['openid_password']
        email = request.POST['email']
        
        #m = Profile.get_object(username__exact = usernm)
        #m = Profile.objects.get(user__exact = usernm)
        try:
            #m = Profile.objects.get(username__exact = usernm)
            User.objects.get(username__exact=usernm)
            return HttpResponse("The username already used.")
            #return HttpResponseRedirect(reverse('scipio_login') + '?redirect=' + request.path)
        except User.DoesNotExist:
            pass
        
        #from my_django.contrib.auth.models import User
        user = User.objects.create_user(usernm, email, passwd)
        m = user
        m.is_staff = True
        m.save()

        # At this point, user is a User object that has already been saved
        # to the database. You can continue to change its attributes
        # if you want to change other fields.
        Profile(
            user=user,
            # --
            max_posts = 1,
            today_posts = 0,
            # --
            max_topics = 1,
            today_topics = 0,
            # --
            max_edits = 0,
            today_edits = 0,
            # --
            total_posts = 0,
            # --
            carma = 0,
            today_change_carmas = 0,
            max_change_carmas = 0,
            # --
            last_post = datetime.now().date(),
            last_edit = datetime.now().date(),
            # --
            registered_date = datetime.now().date(),
            registered_ip = request.META['REMOTE_ADDR'],
            # --
            max_repos = 0,
            used_repos = 0,
        ).save()
        
        #m = User.objects.get(username=usernm)
        request.session['member_id'] = m.id
        #return HttpResponse("You're logged in.")
    
        # Check that the test cookie worked (we set it below):
        if request.session.test_cookie_worked():

            # The test cookie worked, so delete it.
            request.session.delete_test_cookie()

            # If we didn't post, send the test cookie along with the login form.
            request.session.set_test_cookie()

    return HttpResponseRedirect(post_redirect(request))

    
def is_user_can_add_topic_or_article(request):
    if ('%s' % (request.user,)) == 'AnonymousUser':
        return False
    profile = request.user.cicero_profile

    if profile.last_post < datetime.now().date() and profile.today_posts != 0:
        profile.today_posts = 0
        if profile.total_posts < 10:
            profile.max_posts = 1
        else:
            profile.max_posts = 4 + (profile.total_posts / 10) + (profile.carma / 5)
            if profile.max_posts < 1:
                profile.max_posts = 1
        profile.save()
        
    if profile.last_edit < datetime.now().date() and profile.today_edits != 0:
        profile.today_edits = 0
        if profile.total_posts < 40:
            profile.max_edits = 0
        else:
            profile.max_edits = -3 + (profile.total_posts / 10) + (profile.carma / 10)
        profile.save()

    if profile.last_edit < datetime.now().date() and profile.today_change_carmas != 0:
        profile.today_change_carmas = 0
        profile.max_change_carmas = (profile.total_posts / 500) + (profile.carma / 20)
        profile.save()

    is_can = ( profile.user.is_superuser or 
               profile.moderator or
               ((not profile.is_banned) and profile.today_posts < profile.max_posts)
             )
    return is_can


def inc_article_cntr(request):
    if ('%s' % (request.user,)) == 'AnonymousUser':
        return
    profile = request.user.cicero_profile
    
    profile.today_posts += 1
    profile.total_posts += 1
    profile.last_post = datetime.now().date()
    
    profile.user_agent = request.META['HTTP_USER_AGENT']
    profile.last_ip = request.META['REMOTE_ADDR']
    
    profile.save()


@never_cache
@condition(caching.user_etag, caching.latest_change)
def articles_list(request, *args, **kwargs):
    if 'application/xrds+xml' in request.META.get('HTTP_ACCEPT', ''):
        return render_to_response(request, 'cicero/yadis.xml', {
            'return_to': absolute_url(reverse(auth)),
        }, mimetype='application/xrds+xml')

    kwargs['extra_context'] = {'groups': _get_left_side_cont()}

    return object_list(request, *args, **kwargs)


@never_cache
@condition(caching.user_etag, caching.latest_change)
def index(request, *args, **kwargs):
    if 'application/xrds+xml' in request.META.get('HTTP_ACCEPT', ''):
        return render_to_response(request, 'cicero/yadis.xml', {
            'return_to': absolute_url(reverse(auth)),
        }, mimetype='application/xrds+xml')

    kwargs['extra_context'] = {'groups': _get_left_side_cont(), 'summary': _get_summary_cont(request)}

    return object_list(request, *args, **kwargs)

@never_cache
@condition(caching.user_etag, caching.latest_change)
def forum(request, slug, **kwargs):
    forum = get_object_or_404(Forum, slug=slug)
    if request.method == 'POST' and is_user_can_add_topic_or_article(request):
        form = forms.TopicForm(forum, request.user, request.META.get('REMOTE_ADDR'), request.POST)
        if form.is_valid():
            article = form.save()
            inc_article_cntr(request)
            return _process_new_article(request, article, True, True)
    else:
        form = forms.TopicForm(forum, request.user, request.META.get('REMOTE_ADDR'))

    kwargs['queryset'] = forum.topic_set.filter(spam_status='clean', is_forum=True).select_related('forum')
    kwargs['extra_context'] = {'forum': forum, 'form': form, 'page_id': 'forum', 
                               'groups': _get_left_side_cont(),
                               'summary': _get_summary_cont(request),
                               'is_user_can_add_topic_or_article': is_user_can_add_topic_or_article(request)}
    return object_list(request, **kwargs)

@never_cache
@condition(caching.user_etag, caching.latest_change)
def topic(request, slug, id, **kwargs):
    topic = get_object_or_404(Topic, forum__slug=slug, pk=id)
    if request.method == 'POST' and is_user_can_add_topic_or_article(request):
        form = forms.ArticleForm(topic, request.user, request.META.get('REMOTE_ADDR'), request.POST)
        if form.is_valid():
            article = form.save()
            inc_article_cntr(request)
            r = _process_new_article(request, article, False, True)
            return r
    else:
        form = forms.ArticleForm(topic, request.user, request.META.get('REMOTE_ADDR'))
    if request.user.is_authenticated():
        profile = request.user.cicero_profile
        is_can_change_carmas = profile.today_change_carmas < profile.max_change_carmas
        changed = profile.add_read_articles(topic.article_set.all())
        if changed:
            profile.save()
            caching.invalidate_by_user(request)
    else:
        is_can_change_carmas = False

    kwargs['queryset'] = topic.article_set.filter(spam_status='clean', is_forum=True).select_related()
    kwargs['extra_context'] = {'topic': topic, 'form': form, 'page_id': 'topic', 'show_last_link': True, 
                               'groups': _get_left_side_cont(),
                               'summary': _get_summary_cont(request),
                               'is_user_can_add_topic_or_article': is_user_can_add_topic_or_article(request),
                               'is_can_change_carmas': is_can_change_carmas }
    return object_list(request, **kwargs)

    
@never_cache
#@condition(caching.user_etag, caching.latest_change)
def carma(request, tgt_user, inc_dec, **kwargs):
    #print tgt_user
    u = '%s' % (request.user,)
    #print u
    if request.user.is_authenticated() and tgt_user != u and (inc_dec == "inc" or inc_dec == "dec"):
        profile = request.user.cicero_profile
        is_can_change_carmas = profile.today_change_carmas < profile.max_change_carmas
        #print is_can_change_carmas
        if is_can_change_carmas:
            profile.today_change_carmas += 1
            profile.save()
            
            from my_django.contrib.auth.models import User
            try:
                u = User.objects.get(username__exact=tgt_user)
                profile = Profile.objects.filter(user=u).get()
                if inc_dec == "inc":
                    profile.carma += 1
                else:
                    profile.carma -= 1
                profile.save()
            except User.DoesNotExist:
                pass

            caching.invalidate_by_user(request)
    else:
        is_can_change_carmas = False

    #kwargs['queryset'] = topic.article_set.filter(spam_status='clean', is_forum=True).select_related()
    #kwargs['extra_context'] = {'topic': topic, 'form': form, 'page_id': 'topic', 'show_last_link': True, 
    #                           'groups': _get_left_side_cont(),
    #                           'is_user_can_add_topic_or_article': is_user_can_add_topic_or_article(request)}
    #return object_list(request, **kwargs)
    if is_can_change_carmas:
        return HttpResponseRedirect(post_redirect(request))  #HttpResponse(u"carma of %s succesfully changed" % (tgt_user,))
    else:
        return HttpResponse(u"you can not change this carma")

 

def user_authenticated(sender, user, op=None, acquire=None, **kwargs):
    if op == 'login':
        caching.invalidate_by_user(sender)
    if acquire is not None:
        try:
            article = Article.objects.get(pk=acquire)
            article.author = user.cicero_profile
            article.save()
            return _process_new_article(
                sender,
                article,
                article.topic.article_set.count() == 1,
                False
            )
        except Article.DoesNotExist:
            pass

def user_topics(request, id):
    profile = get_object_or_404(Profile, pk=id)
    return object_list(request,
        queryset=profile.topics(),
        allow_empty=True,
        paginate_by=settings.CICERO_PAGINATE_BY,
        template_name='cicero/user_topics.html',
        extra_context={
            'author_profile': profile,
        }
    )

def _profile_forms(request):
#    cicero_profile = request.user.cicero_profile
#    try:
#        scipio_profile = request.user.scipio_profile
#    except ScipioProfile.DoesNotExist:
#        scipio_profile = None
    return {
        'openid': AuthenticationForm(request, initial={'openid_identity': "тут надо показать залогинен ли"}), #scipio_profile and scipio_profile.openid}),
#        'openid': AuthForm(request.session, initial={'openid_identity': "тут надо показать залогинен ли"}), #scipio_profile and scipio_profile.openid}),
#        'personal': scipio_profile and ProfileForm(instance=scipio_profile),
        'settings': forms.SettingsForm(instance=cicero_profile),
    }

def _profile_page(request, forms):
    data = {'page_id': 'edit_profile'}
    data.update(forms)
    return render_to_response(request, 'cicero/profile_form.html', data)

@login_required
def edit_profile(request):
    return _profile_page(request, _profile_forms(request))

@login_required
@require_POST
def change_openid(request):
    forms = _profile_forms(request)
    form = forms['openid'].__class__(request.session, request.POST)
    forms['openid'] = form
    if form.is_valid():
        after_auth_redirect = form.auth_redirect(post_redirect(request), {'op': 'change_openid'})
        return HttpResponseRedirect(after_auth_redirect)
    return _profile_page(request, forms)

def change_openid_complete(sender, user, op=None, **kwargs):
    if op == 'change_openid':
        if sender.user == user:
            return
        # move articles to current user in case user has already existed
#        user.cicero_profile.article_set.all().update(author=sender.user.cicero_profile)
#        profile, created = ScipioProfile.objects.get_or_create(user=sender.user)
#        profile.openid = user.scipio_profile.openid
#        profile.openid_server = user.scipio_profile.openid_server
        user.delete() # must delete new user before profile.save() to not violate openid uniqueness
        profile.save()
#        sender.user.cicero_profile.generate_mutant()

@login_required
@require_POST
def post_profile(request, form_name):
    forms = _profile_forms(request)
    profile = {
#        'settings': request.user.cicero_profile,
#        'personal': request.user.scipio_profile,
    }[form_name]
    form = forms[form_name].__class__(request.POST, instance=profile)
    forms[form_name] = form
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('../')
    return _profile_page(request, forms)

@require_POST
def mark_read(request, slug=None):
    qs = Article.objects.all()
    if slug:
        qs = qs.filter(topic__forum__slug=slug)
    if request.user.is_authenticated():
        profile = request.user.cicero_profile
        profile.add_read_articles(qs)
        profile.save()
        caching.invalidate_by_user(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER') or '../')

@require_POST
def article_preview(request):
    form = forms.PreviewForm(request.POST)
    if not form.is_valid():
        return JSONResponse({'status': 'invalid'})
    return JSONResponse({'status': 'valid', 'html': form.preview()})

@login_required
def article_edit(request, id):
    article = get_object_or_404(Article, pk=id)
    if not request.user.cicero_profile.can_change_article(article):
        return HttpResponseForbidden('Нет прав для редактирования')
    if request.method == 'POST':
        form = forms.ArticleEditForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            caching.invalidate_by_article(article.topic.forum.slug, article.topic.id)
            url = '%s#%s' % (reverse(topic, args=(article.topic.forum.slug, article.topic.id)), article.id)
            return HttpResponseRedirect(url)
    else:
        form = forms.ArticleEditForm(instance=article)
    return render_to_response(request, 'cicero/article_edit.html', {
        'form': form,
        'article': article,
    })

@login_required
def article_delete(request, id):
    article = get_object_or_404(Article, pk=id)
    if not request.user.cicero_profile.can_change_article(article):
        return HttpResponseForbidden('Нет прав для удаления')
    article.deleted = datetime.now()
    article.save()
    caching.invalidate_by_article(article.topic.forum.slug, article.topic.id)
    if article.topic.article_set.count():
        return HttpResponseRedirect(reverse(topic, args=(article.topic.forum.slug, article.topic.id)))
    else:
        article.topic.deleted = datetime.now()
        article.topic.save()
        return HttpResponseRedirect(reverse(forum, args=(article.topic.forum.slug,)))

@login_required
def article_undelete(request, id):
    try:
        article = Article.deleted_objects.get(pk=id)
    except Article.DoesNotExist:
        raise Http404
    if not request.user.cicero_profile.can_change_article(article):
        return HttpResponseForbidden('Нет прав для восстановления')
    Article.deleted_objects.filter(pk=id).update(deleted=None)
    try:
        article_topic = Topic.deleted_objects.get(pk=article.topic_id)
        Topic.deleted_objects.filter(pk=article.topic_id).update(deleted=None)
    except Topic.DoesNotExist:
        article_topic = article.topic
    caching.invalidate_by_article(article_topic.forum.slug, article_topic.id)
    return HttpResponseRedirect(reverse(topic, args=(article_topic.forum.slug, article_topic.id)))

@login_required
def deleted_articles(request, user_only):
    profile = request.user.cicero_profile
    if not user_only and not profile.moderator:
        return HttpResponseForbidden('Нет прав просматривать все удаленные статьи')
    queryset = Article.deleted_objects.select_related()
    if user_only:
        queryset = queryset.filter(author=profile)
    kwargs = {
        'queryset': queryset,
        'template_name': 'cicero/article_deleted_list.html',
        'extra_context': {
            'user_only': user_only and profile,
        },
    }
    kwargs.update(generic_info)
    return object_list(request, **kwargs)

@login_required
def article_publish(request, id):
    if not request.user.cicero_profile.moderator:
        return HttpResponseForbidden('Нет прав публиковать спам')
    article = get_object_or_404(Article, pk=id)
    #antispam.conveyor.submit_ham(article.spam_status, article=article)
    article.set_spam_status('clean')
    if not article.from_guest():
        pass
#        scipio_profile = article.author.user.scipio_profile
#        if scipio_profile.spamer is None:
#            scipio_profile.spamer = False
#            scipio_profile.save()
    caching.invalidate_by_article(article.topic.forum.slug, article.topic.id)
    return HttpResponseRedirect(reverse(spam_queue))

@login_required
def article_spam(request, id):
    if not request.user.cicero_profile.moderator:
        return HttpResponseForbidden('Нет прав определять спам')
    article = get_object_or_404(Article, pk=id)
    if not article.from_guest():
        pass
#        scipio_profile = article.author.user.scipio_profile
#        if scipio_profile.spamer is None:
#            scipio_profile.spamer = True
#            scipio_profile.save()
    #antispam.conveyor.submit_spam(article=article)
    slug, topic_id = article.topic.forum.slug, article.topic.id
    article.delete()
    caching.invalidate_by_article(slug, topic_id)
    if Topic.objects.filter(pk=topic_id).count():
        return HttpResponseRedirect(reverse(topic, args=(slug, topic_id)))
    else:
        return HttpResponseRedirect(reverse(forum, args=(slug,)))

@login_required
def delete_spam(request):
    if not request.user.cicero_profile.moderator:
        return HttpResponseForbidden('Нет прав удалять спам')
    Article.objects.exclude(spam_status='clean').delete()
    Topic.objects.exclude(spam_status='clean').delete()
    return HttpResponseRedirect(reverse(spam_queue))

@login_required
def spam_queue(request):
    if not request.user.cicero_profile.moderator:
        return HttpResponseForbidden('Нет прав просматривать спам')
    queryset = Article.objects.exclude(spam_status='clean').order_by('-created').select_related()
    kwargs = {
        'queryset': queryset,
        'template_name': 'cicero/spam_queue.html',
    }
    kwargs.update(generic_info)
    return object_list(request, **kwargs)

@login_required
def topic_edit(request, topic_id):
    t = get_object_or_404(Topic, pk=topic_id)
    if not request.user.cicero_profile.can_change_topic(t):
        return HttpResponseForbidden('Нет прав редактировать топик')
    if request.method == 'POST':
        form = forms.TopicEditForm(request.POST, instance=t)
        if form.is_valid():
            form.save()
            caching.invalidate_by_article(t.forum.slug, t.id)
            return HttpResponseRedirect(reverse(topic, args=[t.forum.slug, t.id]))
    else:
        form = forms.TopicEditForm(instance=t)
    return render_to_response(request, 'cicero/topic_edit.html', {
        'form': form,
        'topic': t,
    })

@login_required
def topic_spawn(request, article_id):
    if not request.user.cicero_profile.moderator:
        return HttpResponseForbidden('Нет прав отщеплять топики')
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        form = forms.SpawnForm(article, request.POST)
        if form.is_valid():
            new_topic = form.save()
            return HttpResponseRedirect(reverse(topic, args=(new_topic.forum.slug, new_topic.id)))
    else:
        form = forms.SpawnForm(article)
    return render_to_response(request, 'cicero/spawn_topic.html', {
        'form': form,
        'article': article,
    })

@login_required
def topic_to_article(request, article_id):
    if not request.user.cicero_profile.moderator:
        return HttpResponseForbidden('Нет прав отщеплять топики')
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        form = forms.ToArticleForm(article, request.POST)
        if form.is_valid():
            new_topic = form.save()
            return HttpResponseRedirect(reverse(topic, args=(new_topic.forum.slug, new_topic.id)))
    else:
        form = forms.ToArticleForm(article)
    return render_to_response(request, 'cicero/topic_to_article.html', {
        'form': form,
        'article': article,
    })

class SearchUnavailable(Exception):
        pass

class SphinxObjectList(object):
    def __init__(self, sphinx, term):
        self.sphinx = sphinx
        self.term = term

    def _get_results(self):
        results = self.sphinx.Query(self.term)
        if results == {}:
            raise SearchUnavailable()
        if results is None:
            results = {'total_found': 0, 'matches': []}
        return results

    def count(self):
        if not hasattr(self, 'results'):
            return self._get_results()['total_found']
        return self.results['total_found']

    def __len__(self):
        return self.count()

    def __getitem__(self, k):
        if hasattr(self, 'result'):
            raise Exception('Search result already available')
        self.sphinx.SetLimits(k.start, (k.stop - k.start) or 1)
        self.results = self._get_results()
        ids = [m['id'] for m in self.results['matches']]
        return Topic.objects.filter(id__in=ids)

def search(request, slug):
    forum = get_object_or_404(Forum, slug=slug)
    try:
        try:
            from sphinxapi import SphinxClient, SPH_MATCH_EXTENDED, SPH_SORT_RELEVANCE
        except ImportError:
            raise SearchUnavailable()
        term = request.GET.get('term', '').encode('utf-8')
        if term:
            sphinx = SphinxClient()
            sphinx.SetServer(settings.CICERO_SPHINX_SERVER, settings.CICERO_SPHINX_PORT)
            sphinx.SetMatchMode(SPH_MATCH_EXTENDED)
            sphinx.SetSortMode(SPH_SORT_RELEVANCE)
            sphinx.SetFilter('gid', [forum.id])
            paginator = Paginator(SphinxObjectList(sphinx, term), settings.CICERO_PAGINATE_BY)
            try:
                page = paginator.page(request.GET.get('page', '1'))
            except InvalidPage:
                raise Http404
        else:
            paginator = Paginator([], 1)
            page = paginator.page(1)
        return render_to_response(request, 'cicero/search.html', {
            'page_id': 'search',
            'forum': forum,
            'term': term,
            'paginator': paginator,
            'page_obj': page,
            'query_dict': request.GET,
        })
    except SearchUnavailable:
        raise
        return render_to_response(request, 'cicero/search_unavailable.html', {})
