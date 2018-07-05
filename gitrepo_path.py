import os

gitconf_path = os.path.abspath(os.path.dirname(__file__) + '/repo/git/')
#HTDIGEST_FILE = gitconf_path + "/gitweb-users.htdigest"

#with open(gitconf_path + "/repos.txt") as f:
#    KLAUS_REPO_PATHS = [line.rstrip('\n') for line in f]

#KLAUS_REPO_PATHS = [
#    PROJECT_ROOT + '/gitrepo/*',
#]

REPO_HOME = gitconf_path
if not os.path.exists(REPO_HOME):# ingore REPO_HOME is a file
    os.mkdir(REPO_HOME)
