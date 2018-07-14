import os
from my_django.conf import settings

self_repo_name = '.self'

REPO_HOME = settings.REPO_HOME + '/' + self_repo_name
PROJECT_ROOT = settings.PROJECT_ROOT

if (not os.path.isdir(REPO_HOME)) or (not os.path.isdir(REPO_HOME + '/.git')):
    from my_sh import sh
    from my_sh.sh.contrib import git
    
    from my_django.contrib.auth.models import User
    user = User.objects.get(is_superuser=1)
    username = user.username

    repo_path = REPO_HOME
    #sh.mkdir(repo_path)
    sh.ln('-sf', PROJECT_ROOT, repo_path)
    sh.cd(repo_path)
    git.init()
    git.add('-f', 'db/.noremove')
    git.add('-f', 'repo/git/.noremove')
    git.add('-f', 'repo/hg/.noremove')
    git.add('.gitignore')
    git.add('.')
    try:
        git.commit('-m', 'first-commit')
    except:
        git.config('--global', 'user.email', user.email)
        git.config('--global', 'user.name', username)
        try:
            git.commit('-m', 'first-commit')
        except:
            pass
    try:
        from my_klaus.models import Repo
        try:
            repo = Repo.objects.get(name=self_repo_name)
            repo.users_owner=username
            repo.users_read=username
            repo.users_write=username
            repo.save()
        except:
            repo = Repo.objects.create(name=self_repo_name, url=repo_path, users_owner=username, users_read=username, users_write=username)
    except:
        pass
