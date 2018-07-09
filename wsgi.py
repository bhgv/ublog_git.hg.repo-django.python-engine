import os, sys
from string import *

MY_PATH = os.path.normpath(os.path.dirname(__file__))
# adjust python path if not a system-wide install:
sys.path.append(MY_PATH)

sys.stdout = sys.stderr

# Uncomment to send python tracebacks to the browser if an error occurs:
import cgitb
cgitb.enable()

# If you'd like to serve pages with UTF-8 instead of your default
# locale charset, you can do so by uncommenting the following lines.
# Note that this will cause your .hgrc files to be interpreted in
# UTF-8 and all your repo files to be displayed using UTF-8.
#
#import os
os.environ["HGENCODING"] = "UTF-8"

import os.path
os.environ['PROJECT_ROOT'] = MY_PATH

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from my_klaus.my_git_wsgi_wrapper import MyGitFileSystemBackend
from my_klaus import httpauth

import my_django.core.handlers.wsgi

#_application = my_django.core.handlers.wsgi.WSGIHandler()
def application(environ, start_response):
    import my_dulwich.web

    environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']

    _application = my_django.core.handlers.wsgi.WSGIHandler()

    ## `path -> Repo` mapping for Dulwich's web support
    #dulwich_backend = my_dulwich.server.DictBackend(
    #    dict(('/'+name, repo) for name, repo in app.repos.items())
    #)
    from gitrepo_path import REPO_HOME
    path = os.path.abspath(os.path.dirname(REPO_HOME))
    dulwich_backend = MyGitFileSystemBackend(
        path
    )
    # Dulwich takes care of all Git related requests/URLs
    # and passes through everything else to klaus
    dulwich_wrapped_app = my_dulwich.web.make_wsgi_chain(
        backend=dulwich_backend,
        fallback_app=_application,
    )
    #dulwich_wrapped_app = utils.ProxyFix(dulwich_wrapped_app)
    
    PATTERNS = [
        r'^/([^/]*/)*(info/refs\?service=git-receive-pack)$',
        #r'^/[^/]+/(info/refs\?service=git-receive-pack)$',
        r'^/([^/]*/)*(info/refs\?service=git-upload-pack)$',
    ]
    dulwich_wrapped_app = httpauth.CiceroKlausUserHttpAuthMiddleware(
        wsgi_app=dulwich_wrapped_app,
        routes=PATTERNS,
    )

    return dulwich_wrapped_app(environ, start_response)
#    return _application(environ, start_response)
   
