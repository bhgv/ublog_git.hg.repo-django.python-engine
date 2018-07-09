import os

gitconf_path = os.path.abspath(os.path.dirname(__file__) + '/repo/git/')
#with open(gitconf_path + "/repos.txt") as f:
#    KLAUS_REPO_PATHS = [line.rstrip('\n') for line in f]
REPO_HOME = gitconf_path
if not os.path.exists(REPO_HOME):
    os.mkdir(REPO_HOME)
