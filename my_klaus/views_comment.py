from my_django.http import HttpResponse
from my_django.views.decorators.csrf import csrf_exempt
from my_sh import sh
from my_sh.sh.contrib import git
from my_klaus.models import Repo, Comment
from my_django.conf import settings
from my_klaus.repo import fresh_repo_list

@csrf_exempt
def post_comment(request):
    data = request.POST
    path = data['path']
    repo_url = data['repo_url']
    repo = Repo.objects.get(url=repo_url)
    line = data['line']
    text = data['text']
    rev = data['rev']
    Comment.objects.create(repo = repo,file_path=path,rev=rev,line=line,content=text)
    return HttpResponse('ok')

@csrf_exempt
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
    return HttpResponse('ok')