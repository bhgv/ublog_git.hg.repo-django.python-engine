#from my_django.http import HttpResponse
from my_django.http import HttpResponseNotAllowed, HttpResponseNotModified, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, Http404

from my_django.contrib.auth.forms import AuthenticationForm

from my_django.views.decorators.csrf import csrf_exempt
from my_sh import sh
from my_sh.sh.contrib import git
from my_klaus.models import Repo, Comment
from my_django.conf import settings
from my_klaus.repo import fresh_repo_list


def post_redirect(request):
    return request.POST.get('redirect', request.META.get('HTTP_REFERER', '/'))


def login_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponse(u'You should login first!')
        return func(request, *args, **kwargs)
    return wrapper


#    if request.user.is_authenticated():
#        usernm = request.user.username
#        return HttpResponse("You already logged %s." % (usernm,))
#    else:
#        if request.method == 'POST': # If the form has been submitted...
#            #form = LoginForm(request.POST) # A form bound to the POST data
#            #if form.is_valid(): # All validation rules pass
#            
#            from my_django.contrib.auth import authenticate, login
#            
#            user = authenticate(username=usernm, password=passwd)
#            if user is not None:
#                if user.is_active:
#                    # Redirect to a success page.
#                    login(request, user)
                    #return HttpResponse(u'ok')
                    #return HttpResponseRedirect(reverse('scipio_login') + '?redirect=' + request.path)
                    #print post_redirect(request)
#                    return HttpResponseRedirect(post_redirect(request))



@csrf_exempt
@login_required
def post_comment(request):
    data = request.POST
    path = data['path']
    repo_url = data['repo_url']
    repo = Repo.objects.get(url=repo_url)
    line = data['line']
    text = data['text']
    rev = data['rev']
    Comment.objects.create(repo = repo,file_path=path,rev=rev,line=line,content=text)
    #return HttpResponse('ok')
    return HttpResponseRedirect(post_redirect(request))


@csrf_exempt
@login_required
def clone_repo(request):
    data = request.POST
    repo_url = data['repo_url']
    repo_home = settings.REPO_HOME
    sh.cd(repo_home)
    try:
        git.clone(repo_url)
    except:
        sh.mkdir(repo_url)
        sh.cd(repo_url)
        git.init()
    fresh_repo_list()
    repo_name = repo_url.split('/')[-1][:-4]
    Repo.objects.create(name=repo_name,url=repo_url)
    #return HttpResponse('ok')
    return HttpResponseRedirect(post_redirect(request))


@csrf_exempt
@login_required
def update_settings(request, *args, **kwargs):
    data = request.POST
    owners = data['perm_owners']
    readers = data['perm_readers']
    writers = data['perm_writers']
    
    repo_url = data['repo_url'] # or 
    repo_name = kwargs['repo']
    try:
        from cicero.models import Profile
        
        repo_obj = Repo.objects.get(name=repo_name)

        profile = request.user.cicero_profile
        
        is_banned = profile.is_banned
        if is_banned:
            return HttpResponseRedirect(post_redirect(request))
        
        is_superuser = profile.user.is_superuser
        is_moderator = profile.moderator

        uowners = repo_obj.users_owner.split('\n')
        
        if is_superuser or is_moderator or (user in uowners):
            repo_obj.users_owner = owners
            repo_obj.users_read = readers
            repo_obj.users_write = writers
            repo_obj.save()
            
    except:
        pass
    #return HttpResponse('ok')
    return HttpResponseRedirect(post_redirect(request))
